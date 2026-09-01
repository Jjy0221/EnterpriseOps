from langchain_core.tools import tool
from app.services.rag import retrieve_with_rerank
from app.services.ticket_service import(
    get_ticket as get_ticket_service,
    create_ticket as create_ticket_service,
)
from app.config import settings

@tool
def search_knowledge(question:str) -> dict:
    """
    从企业知识库中检索与用户问题最相关的知识片段。
    适用于企业制度、账号、VPN、API、运维流程等知识类问题
    """

    hits = retrieve_with_rerank(
        question,
        top_k = settings.top_k,
        candidate_k = 10
    )

    return{
        "question" : question,
        "hits" : hits,
    }

@tool
def get_ticket(ticket_id : str) -> dict:
    """
    根据工单编号查询工单信息。
    当用户询问某个具体工单的标题、描述或当前状态时使用
    """
    ticket = get_ticket_service(ticket_id)

    if ticket is None:
        return{
            "found" : False,
            "message" : f"未找到工单{ticket_id}"
        }
    return{
            "found" : True,
            "ticket_id" : ticket.ticket_id,
            "title" : ticket.title,
            "description" : ticket.description,
            "status" : ticket.status,

    }

@tool
def create_ticket(title:str, description : str = "") -> dict:
    """
    创建新的企业服务工单。
    仅当用户明确表达“创建、提交、新建、登记工单”等意图时使用。
    如果用户只是询问故障解决办法，不应调用此工具。
    """
    ticket = create_ticket_service(
        title = title,
        description = description,
    )

    return{
        "created": True,
        "ticket_id":ticket.ticket_id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
    }