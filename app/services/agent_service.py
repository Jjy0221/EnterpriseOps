from functools import lru_cache
from langchain.agents import create_agent

from app.services.llm import get_chat_model
from app.services.agent_tools import (
    search_knowledge,
    get_ticket,
    create_ticket,
)

@lru_cache
def get_agent():
    system_prompt = (
        "你是 EnterpriseOps Copilot 企业内部智能助手。"
        "知识规则、VPN、账号、API、运维流程等问题调用 search_knowledge。"
        "用户要求查询具体工单时调用 get_ticket。"
        "只有当用户明确要求创建、提交、新建或登记工单时，才调用 create_ticket。"
        "如果用户只是询问故障解决方法，不要擅自创建工单。"
        "不要编造工具没有返回的信息。"
    )
    return create_agent(
        model=get_chat_model(),
        tools=[search_knowledge, get_ticket, create_ticket],
        system_prompt=system_prompt,
    )


def run_agent(message: str) -> str:
    result = get_agent().invoke(
        {"messages":
             [{"role": "user",
               "content": message}]}
    )
    return result["messages"][-1].content
