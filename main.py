import streamlit as st
import openai
import json
import os
import time
from streamlit_modal import Modal

# 设置 OpenAI API 密钥
openai.api_key = "sk-db44eee9cc0a494d84595baeb33dd58f"
def llm(prompt):
    try:
        client = openai.OpenAI(api_key=openai.api_key, base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=False
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

my_modal = Modal(title="", key="modal_key", max_width=500)
# 定义大模型节点类
class ModelNode:
    def __init__(self, name, system_message,api):
        self.name = name
        self.system_message = system_message
        self.api=api
        self.messages = []
    
    
    def run(self):
        pass
    def llm(self, prompt):
        try:
            client = openai.OpenAI(api_key=openai.api_key, base_url="https://api.deepseek.com")

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

# 初始化大模型节点
if "model_nodes" not in st.session_state:
    st.session_state.model_nodes = {}
if "selected_nodes" not in st.session_state:
    st.session_state.selected_nodes = []
if "history" not in st.session_state:
    st.session_state.history=[]
if "mode" not in st.session_state:
    st.session_state.mode="normal"
if "now_nodes" not in st.session_state:
    st.session_state.now_nodes=[]
@st.dialog("新建节点")
def create_node():
    new_node_name = st.text_input("输入新节点名称")
    new_system_message = st.text_input("输入新节点的人设")
    new_node_api = st.text_input("输入新节点的api")
    submit=st.button("创建节点", key="confirm")
    print(submit)
    if submit and new_system_message and new_node_name:
        print(2)
        st.session_state.model_nodes[new_node_name] = ModelNode(new_node_name, new_system_message,new_node_api)
        print(st.session_state.model_nodes)
        st.rerun()


# 设置 Streamlit 页面标题

# 新建节点按钮

    

# # 显示所有节点按钮
with st.sidebar:
    if st.button("新建节点",key="123"):
       create_node()
    if st.button("调度中心"):
        st.session_state.mode="agent"
    num_columns = 3

    # 计算需要多少行
    buttons=[node_name for node_name,_ in st.session_state.model_nodes.items()]
    num_rows = (len(buttons) + num_columns - 1) // num_columns

    # 创建行和列布局
    for row in range(num_rows):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            button_idx = row * num_columns + col_idx
            if button_idx < len(buttons):
                with cols[col_idx]:
                        if st.button(buttons[button_idx]):
                            st.session_state.mode="normal"
                            if buttons[button_idx] in st.session_state.selected_nodes:
                                st.session_state.selected_nodes.remove(buttons[button_idx])
                            else:
                                st.session_state.selected_nodes.append(buttons[button_idx])
                    # st.button(buttons[button_idx])
    # for node_name,value in st.session_state.model_nodes.items():
    #     print(node_name)
    if st.session_state.mode=="agent":
        st.session_state.now_nodes=[value for _,value in st.session_state.model_nodes.items()]
        st.markdown(f"当前选择的节点是  调度中心")
    else:
        st.session_state.now_nodes= st.session_state.selected_nodes
        st.markdown(f"当前选择的节点是  {st.session_state.selected_nodes}")
    

# # 显示当前节点的对话历史
# for node_name in st.session_state.selected_nodes:
#     current_node = st.session_state.model_nodes[node_name]
#     st.subheader(f"节点: {node_name}")
#     for message in current_node.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
def user_chat(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.history.append({"role":"user","content":prompt})
def assistant_chat(node_name,assistant_response):
    with st.chat_message("assistant"):
                st.markdown(f"""## {node_name}""")
                st.markdown(assistant_response)
                st.session_state.history.append({"role":"assistant","content":f"""## {node_name}
    {assistant_response}
    """})
def normal(prompt):
      user_chat(prompt)
    # 将用户输入添加到当前节点的对话历史中
      for node_name in st.session_state.selected_nodes:
        current_node = st.session_state.model_nodes[node_name]
        # current_node.messages.append({"role": "user", "content": prompt})

        # 显示用户输入

        assistant_response = current_node.llm(prompt)

        # 将模型的回复添加到当前节点的对话历史中
        # current_node.messages.append({"role": "assistant", "content": assistant_response})

        # 显示模型的回复
        assistant_chat(node_name,assistant_response)

        st.rerun()   

def agent1():
    ##写死
    return
def agent2(prompt):
    user_chat(prompt)
    nodes="\n".join([f"{index}.{item.name}: {item.system_message}" for index,item in  enumerate(st.session_state.now_nodes)])
    ##不写死
    json_mode={
        "分配的任务":["节点名","节点名"]
    }
    agent_res=llm(f"""你是一个任务调度机器人，你要根据我的输入以及每个节点的功能，然后给节点安排任务，你的输出是json格式:{json.dumps(json_mode)}
    例如：
    输入:请对目标人物进行围捕。
    节点:1.无人机:具有飞行能力。
        2.无人车：具有陆地运动能力。
        3.机器狗: 具有陆地智能运动能力。
    输出：{{
        "天空追踪":["无人机"]
        "陆地追踪":["机器狗","无人车"]}}

    现在正式开始任务
    输入：{prompt}
    节点:{nodes}
    输出:
""").replace("```","").replace("json","")
    print("agent_res:",agent_res)
    agent_res=json.loads(agent_res)
    system_print_agent_res=[f"{'和'.join(value)} 分配到了任务 {key} "for key,value in agent_res.items()]
    assistant_chat("系统","\n".join(system_print_agent_res))
    time.sleep(2)
    for task,node_names in agent_res.items():
        if len(node_names)==1:
            assistant_chat(node_names[0],f"接受任务: {task}")
        elif len(node_names)>1:
            for node_name in node_names:
                assistant_chat(node_name,f"存在同一任务，需要细化任务")
            first_chat=llm(f"""
{nodes}

请注意：{",".join(node_names)} 只有这些能力，没有其他功能，超出能力之外的能力，两者都无法执行。

现在 {",".join(node_names)}  要协同去完成一个任务:"{prompt}",  {" 和 ".join(node_names)} 分配到同一个任务:"{task}"，现在你是 {node_names[0]}，请说说应该如何重新分配细化任务，请简要回答
""")
            assistant_chat(node_names[0],f"{first_chat}")
            for node_name in node_names[1:]:
                second_chat=llm(f"""
{nodes}

请注意：{",".join(node_names)} 只有这些能力，没有其他功能，超出能力之外的能力，两者都无法执行。

现在 {",".join(node_names)}  要协同去完成一个任务:"{prompt}",{" 和 ".join(node_names)} 分配到同一个任务:"{task}",现在你是 {node_name},   {node_names[0]}有一个新的任务分配提案，请你判断该提案是否合理，合理则输出 1， 不合理则输出 0 
{node_names[0]}的提案如下: "{first_chat}"

你的输出:
""")
                
                if second_chat== "1":
                    time.sleep(3)
                    assistant_chat(node_name,"我接受该分配提案，准备执行。")


    for  node in st.session_state.now_nodes:
        assistant_chat(node.name,"开始执行")

            
            
    
    return











for item in st.session_state.history:
    role=item['role']
    if role=="user":
        with st.chat_message("user"):
            st.markdown(item['content'])
    if role=="assistant":
        with st.chat_message("assistant"):
            st.markdown(item['content'])
# 获取用户输入
print(f"selected_nodes: {st.session_state.selected_nodes}")
prompt = st.chat_input("你有什么想问的？")
if prompt:
    if st.session_state.mode=="normal":
        normal(prompt)
    if st.session_state.mode=="agent":
        agent2(prompt)



