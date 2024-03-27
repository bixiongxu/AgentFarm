import os
import traceback
import pandas as pd

from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Float
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
from openai import OpenAI
import json
from learning import learn_text
from pymilvus import utility, connections, FieldSchema, CollectionSchema, DataType, Collection
import numpy as np
from assistant import create_assistant, create_thread, summarize_thread_name
import time

with open("config.json", "r") as file:
    config = json.loads(file.read().strip())

# 数据库连接参数
db_config = config['db_config']
# 连接到数据库
engine = create_engine(f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')
openai_client = OpenAI(api_key=config['api_key'])
app = Flask(__name__)
CORS(app)
api = Api(app)

# 初始化向量数据库
connections.connect("default", host=config["vector_db_host"], port=config["vector_db_port"])
collection_name = config["vector_db"]
collection_names = utility.list_collections()

if collection_name in collection_names:
    collection = Collection(name=collection_name)  # 获取已存在的集合
else:
    print(f"Collection {collection_name} does not exist.")
    exit()

def save_chat(is_learning, owner, assistant_id, message_text, files, images):
    # 获取文本消息
    table = "chat_records"
    if is_learning:
        table = "learn_records"
    # 保存内容
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # 准备 SQL 插入语句
        insert_sql = text(f"""
        INSERT INTO {table} (id, owner, assistant_id, created_at) 
        VALUES (:id, :owner, :assistant_id, :created_at)
        """)
        # 准备要插入的数据
        record_id = str(uuid.uuid4())
        created_at = datetime.now()
        # 使用 session 执行 SQL
        session.execute(insert_sql, {
            'id': record_id, 
            'owner': owner,
            'assistant_id': assistant_id, 
            'created_at': created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

        if message_text:
            rewritten_text, embedding = learn_text(openai_client, message_text, config['summarize_limit'])
            insert_sql = text("""
            INSERT INTO record_items (record_item_id, record_id, location, name, type, content, summary, size) 
            VALUES (:record_item_id, :record_id, :location, :name, :type, :content, :summary, :size)
            """)
            record_item_id = str(uuid.uuid4())
            session.execute(insert_sql, {
                'record_item_id': record_item_id, 
                'record_id': record_id, 
                'location': '', 
                'name': '', 
                'type': 'text', 
                'content': message_text, 
                'summary': rewritten_text, 
                'size': 0
            })
            # 开始保存embedding
            insert_result = collection.insert([[str(record_item_id)], [str(assistant_id)], [embedding]])
            collection.load()
            print("Inserted IDs:", insert_result.primary_keys)
            utility.flush_all()

        # 处理图片

        for image in images:
            filename = secure_filename(image.filename)
            filepath = os.path.join('./files', filename)
            image.save(filepath)
            insert_sql = text("""
            INSERT INTO record_items (record_item_id, record_id, location, name, type, content, summary, size) 
            VALUES (:record_item_id, :record_id, :location, :name, :type, :content, :summary, :size)
            """)
            record_item_id = str(uuid.uuid4())
            session.execute(insert_sql, {
                'record_item_id': record_item_id, 
                'record_id': record_id, 
                'location': '', 
                'name': '', 
                'type': 'image', 
                'content': '', 
                'summary': '', 
                'size': image.getbuffer().nbytes
            })
        
        # 处理其他文件
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join('./files', filename)
            print(filepath)
            file.save(filepath)
            insert_sql = text("""
            INSERT INTO record_items (record_item_id, record_id, location, name, type, content, summary, size) 
            VALUES (:record_item_id, :record_id, :location, :name, :type, :content, :summary, :size)
            """)
            record_item_id = str(uuid.uuid4())
            session.execute(insert_sql, {
                'record_item_id': record_item_id, 
                'record_id': record_id, 
                'location': '', 
                'name': '', 
                'type': 'document', 
                'content': '', 
                'summary': '', 
                'size': file.getbuffer().nbytes
            })

        # 提交事务
        session.commit()
        print(f"Inserted new chat record with ID: {record_id}")

    except Exception as e:
        # 如果出现异常，回滚事务
        traceback.print_exc()
        session.rollback()
        print(f"Error occurred: {e}")

    finally:
        # 关闭 session
        session.close()    

class Assistant(Resource):
    def get(self):
        # 获取自己的assitant
        Session = sessionmaker(bind=engine)
        session = Session()
        owner = 'Alice'
        sql = text(f"""
                    select id, assistant_name from assistant where owner='{owner}'
                   """)
        result = session.execute(sql)
        assistants = result.fetchall()
        response = []
        for i in range(len(assistants)):
            # 没有thread，创建一个
            response.append({
                "assistant_id": assistants[i][0],
                "name": assistants[i][1]
            })
            pass
       
        session.close()
        return response, 201
    
    def post(self):
        try:
            # 创建一个assistant
            from_user = 'Alice'
            data = request.get_json()
            assistant = create_assistant(openai_client, from_user, data['name'], data['desc'])
            if assistant:
                Session = sessionmaker(bind=engine)
                session = Session()
                insert_sql = text("""
                    INSERT INTO assistant (id, owner, assistant_name, assistant_desc) 
                    VALUES (:id, :owner, :assistant_name, :assistant_desc)
                """)
                session.execute(insert_sql, {
                    'id': assistant.id, 
                    'owner': from_user, 
                    'assistant_name': assistant.name, 
                    'assistant_desc': assistant.instructions
                })
                session.commit()
                session.close()
            # 构造响应
            response = {
                "assistant_id": assistant.id
            }
            return response, 201
        except: 
            traceback.print_exc()


class Thread(Resource):
    def get(self):
        # 获取某个assistant的threads
        assistant = request.args.get('assistant', None)
        if assistant is None:
            return "No assistant", None
        
        Session = sessionmaker(bind=engine)
        session = Session()
        owner = 'Alice'
        sql = text(f"""
                    select id, thread_name from assistant_thread where from_user='{owner}' and assistant_id='{assistant}' and is_deleted=0 order by updated_at desc limit 10
                   """)
        result = session.execute(sql)
        threads = result.fetchall()
        print(sql)
        print(threads)
        response = []
        for i in range(len(threads)):
            # 没有thread，创建一个
            response.append({ 
                "thread_id": threads[i][0],
                "name": threads[i][1]
            })
            pass
        session.close()
        return response, 201
    
    def post(self):
        try:
            # 创建一个assistant
            from_user = 'Alice'
            # 判断是否在一个thread里面
            
            assistant_id = request.form['assistant_id'] if 'assistant_id' in request.form else None
            if assistant_id is None or assistant_id == '':
                return "Assistant not found! ", 400
            message_text = request.form['message'] if 'message' in request.form else None
            images = request.files.getlist('image')
            files = request.files.getlist('file')
            if message_text is None and len(images) == 0 and len(files) == 0:
                return "You must say something before call me! ", 400
            thread_id = request.form['thread_id'] if 'thread_id' in request.form else None
            if thread_id is None: 
                # 创建一个新的thread
                thread = create_thread(openai_client)
                print("Create a new thread")
                print(thread)
                thread_id = thread.id
                Session = sessionmaker(bind=engine)
                session = Session()
                insert_sql = text("""
                    INSERT INTO assistant_thread (id, from_user, thread_name, assistant_id) 
                    VALUES (:id, :owner, :thread_name, :assistant_id)
                """)
                session.execute(insert_sql, {
                    'id': thread_id, 
                    'owner': from_user, 
                    'thread_name': summarize_thread_name(openai_client, message_text), 
                    'assistant_id': assistant_id
                })
                session.commit()
                session.close()

            # Before creating a message, find out related topic
            rewriten, embedding = learn_text(openai_client, message_text, 1024)
            print(f"assistant_id == '{assistant_id}'")
            
            results = collection.search(
                data=[embedding],  # 查询向量
                anns_field="vector",  # 在哪个向量字段上搜索
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=3,  # 返回最相似的前10个结果
                output_fields=["uuid", "assistant_id"],  # 指定返回的字段，按需更改
                expr = f"assistant_id == '{assistant_id}'"
            )
            print("---------- Vector result ---------")
            print(results)
            prompt_items = []
            query = f"select summary from record_items where record_item_id in ('"
            for query_idx, hits in enumerate(results):
                print(f"Results for query vector #{query_idx + 1}:")
                for rank, hit in enumerate(hits, start=1):
                    print(f"\tRank {rank}, ID: {hit.id}, Distance: {hit.distance}, UUID: {hit.uuid}")
                    prompt_items.append(hit.uuid)
            if len(prompt_items) > 0:
                Session = sessionmaker(bind=engine)
                session = Session()
                query += ("','").join(prompt_items)
                query += "')"
                print(query)
                result = session.execute(text(query))
                prompts = result.fetchall()
                instructions = ""
                for i in range(len(prompts)):
                    # 没有thread，创建一个
                    instructions += f"""
                    \n 参考知识{i+1}:  \n
                    {prompts[i][0]}
                    \n
                    """
                    pass
                print(instructions)     
            message = openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content = instructions + message_text
            )
            
            run = openai_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status in ['queued', 'in_progress', 'cancelling']:
                time.sleep(1) # Wait for 1 second
                run = openai_client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

            if run.status == 'completed': 
                messages = openai_client.beta.threads.messages.list(
                    thread_id=thread_id, 
                    before=message.id
                )

                print(messages)
                response = {
                    "thread_id": thread_id,
                    "messages": json.loads(messages.model_dump_json())
                }

                return response, 201
            else:
                return {"thread_id": thread_id, "messages": []}, 201


        except: 
            traceback.print_exc()


class Learn(Resource):
    def post(self):
        try:
            assistant_id = request.form['assistant_id'] if 'assistant_id' in request.form else None
            if assistant_id is None:
                return "Assistant must be spcified!", 400
            message_text = request.form['message'] if 'message' in request.form else None
            images = request.files.getlist('image')
            files = request.files.getlist('file')
            from_user = 'Alice'
            to_user = 'Bot'
            save_chat(True, from_user, assistant_id, message_text, files, images)
            # 构造响应
            response = {
                "messages": {
                    "data": [
                        {
                            "content": [
                                {
                                    "type": "text", 
                                    "text": {
                                        "value": f"好的，了解。"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            return response, 201
        except: 
            traceback.print_exc()

api.add_resource(Learn, '/learn')
api.add_resource(Assistant, '/agent')
api.add_resource(Thread, '/chat')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port="443", ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True, host='0.0.0.0', port="8089")
    # debug=True, host='0.0.0.0', port="8088", 
