from sqlalchemy import create_engine, text
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType, utility
import numpy as np
import json

with open("config.json", "r") as file:
    config = json.loads(file.read().strip())

# 数据库连接参数
db_config = config['db_config']

# 连接到数据库
engine = create_engine(f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}/{db_config["database"]}')
Session = sessionmaker(bind=engine)
session = Session()
# 检查并创建表

# 一个user可以有多个assistant，这个assistant可以是任何人创建的
# 后面要加上特定的权限

create_user_assistant_table = text("""
CREATE TABLE IF NOT EXISTS assistant (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    assistant_name  VARCHAR(255) NOT NULL,
    assistant_desc TEXT NOT NULL,
    created_at DATETIME, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted INT DEFAULT 0
);
""")
# 使用连接对象来执行SQL语句
session.execute(create_user_assistant_table)

create_assistant_thread_table = text("""
CREATE TABLE IF NOT EXISTS assistant_thread (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    from_user VARCHAR(255) NOT NULL,
    assistant_id VARCHAR(255) NOT NULL,
    thread_name VARCHAR(255) NOT NULL,
    created_at DATETIME, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    is_deleted INT DEFAULT 0
);
""")
# 使用连接对象来执行SQL语句
session.execute(create_assistant_thread_table)


create_learn_records_table = text("""
CREATE TABLE IF NOT EXISTS learn_records (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    assistant_id VARCHAR(255) NOT NULL,
    analyzed INT NOT NULL DEFAULT 0,
    created_at DATETIME, 
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
# 使用连接对象来执行SQL语句
session.execute(create_learn_records_table)

create_chat_records_table = text("""
CREATE TABLE IF NOT EXISTS chat_records (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    from_user VARCHAR(255) NOT NULL,
    assistant_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    is_prompt INT NOT NULL, 
    analyzed INT NOT NULL DEFAULT 0,
    created_at DATETIME, 
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
# 使用连接对象来执行SQL语句
session.execute(create_chat_records_table)

create_chat_record_items_table = text("""
CREATE TABLE IF NOT EXISTS record_items (
    record_item_id VARCHAR(36) NOT NULL PRIMARY KEY,
    record_id VARCHAR(36) NOT NULL,
    location TEXT,
    name VARCHAR(255),
    type ENUM('text', 'image', 'document') NOT NULL,
    content TEXT,
    summary TEXT,
    size BIGINT,
    is_deleted INT default 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
# 使用连接对象来执行SQL语句
session.execute(create_chat_record_items_table)

session.close()

# 连接到Milvus服务器
connections.connect("default", host=config["vector_db_host"], port=config["vector_db_port"])
collection_name = config["vector_db"]
collection_names = utility.list_collections()
collection = None

if collection_name in collection_names:
    collection = Collection(name=collection_name)  # 获取已存在的集合
else:
    dim = config['vector_dim']  # 向量维度
    # 创建字段列表
    fields = [
        FieldSchema(name="uuid", dtype=DataType.VARCHAR, max_length=36, is_primary=True),  # 使用字符串存储UUID
        FieldSchema(name="assistant_id", dtype=DataType.VARCHAR, max_length=36),  # 使用字符串存储UUID
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
    ]
    # 创建集合
    schema = CollectionSchema(fields, "This is an example collection with UUID")
    collection = Collection(name=collection_name, schema=schema, using='default', shards_num=2)

if not collection.has_index():
    print(f"No index found for collection {collection_name}.")
    # 定义索引参数
    index_params = {
        "index_type": "IVF_FLAT",  # 选择一个索引类型，例如 "IVF_FLAT"、"HNSW"、"ANNOY" 等
        "metric_type": "L2",       # 选择一个距离计算类型，例如 "L2" 或 "IP"
        "params": {"nlist": 128}   # 索引构建参数，不同索引类型有不同的参数
    }
    # 为集合创建索引
    collection.create_index(field_name="vector", index_params=index_params)
    print(f"Index created for collection {collection_name}.")
connections.disconnect("default")
    