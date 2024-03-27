"""
学习我的每一次上传的内容
1 对独立文本，直接创建embedding
2 对图片，看图说话后，根据前后的文本内容（发送时间10分钟以内），创建embedding
3 对文档，提取内容后，根据前后的文本内容分段embedding，并对Summary创建embedding

独立文本步骤：
1. 使用精确的时间改写独立文本
2. 如果文本过长，创建summary
3. 创建embedding
"""
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from openai import OpenAI
import json
import tiktoken



def get_embedding(openai_client, text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return openai_client.embeddings.create(input = [text], model=model).data[0].embedding


def learn_text(openai_client, text, summarize_limit):
    # 获取当前日期和时间
    print(text)
    now = datetime.utcnow()
    # 将当前日期格式化为字符串
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')
    rewritten = text
    MODEL = "gpt-4-turbo-preview"
    if len(text) > summarize_limit:
        prompt = f"""
        Please summarize below text to a less than {summarize_limit} words paragraph. {text}
        """
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        rewritten = response.choices[0].message.content    
        print("---- After summarizing -----") 
        print(rewritten)    

    prompt = f"""
    Current UTC time: {date_str}, if below text includes words related to datetime but cannot indicate the exact datetime, please directly rewrite the section with exact time while keeping the same meaning. If there is no, please keep as it. And please output the rewritten part only. \n
    {rewritten}
    """
    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    rewritten = response.choices[0].message.content
    print(rewritten)

    # Start to create embedding
    embedding = get_embedding(openai_client, rewritten)
    print(embedding)
    return rewritten, embedding