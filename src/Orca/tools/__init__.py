from .arxiv_search import ArxivSearchTool
from .dir_reader import DirReaderTool
from .save_to_local import SaveToLocalTool
from .cmd_execute import CmdExecuteTool
from .web_search_zhipu import WebSearchZhipuTool
from .dict_to_multiline_string import DictToMultilineStringTool
from .list_to_multiline_string import ListToMultilineStringTool
from .duckduckgo_websearch import DuckDuckGoWebSearchTool
from .retrival_from_database import RetrivalFromDatabaseTool
from .jina_search import JinaSearchTool
from .jina_read_urls import JinaReadUrlsTool
from .youtube_caption import YouTubeCaptionTool
from .wechatmp_spider import WechatmpSpiderTool
from .paper_with_code import PaperWithCodeTool
from .finance_news_search import FinanceNewsSearchTool
from .browser_use_tool import BrowserUseTool
from .vl_model import VLModelTool
from .code_execute import CodeExecuteTool
from .paper_with_code_full import PaperWithCodeFullTool
from .send_email import SendEmailTool
from .flow_chart import FlowChartTool
from .mermaid_add_picture import MermaidAddPictureTool
from .pdf2pictures import PDF2PicturesTool
from .images_layout_analysis import ImagesLayoutAnalysisTool
from .extract_tables_images_from_images import ExtractTablesImagesFromImagesTool
from .bilibili_retrieval import BiliBiliRetrievalTool
from .pdf_download import PDFDownloadTool
from .pdf_reader import PDFReaderTool
from .twitter_spider import TwitterSpiderTool
from .youtube_retrieval import YouTubeRetrievalTool
from .condition_judge import ConditionJudgeTool
from .orca_dir_reader import OrcaDirReaderTool
from .google_search import GoogleSearchTool

# 工具列表
tools = {
    "arxiv_search": ArxivSearchTool(),
    "dir_reader": DirReaderTool(),
    "save_to_local": SaveToLocalTool(),
    "cmd_execute": CmdExecuteTool(),
    "web_search_zhipu": WebSearchZhipuTool(),
    "dict_to_multiline_string": DictToMultilineStringTool(),
    "list_to_multiline_string": ListToMultilineStringTool(),
    "duckduckgo_websearch": DuckDuckGoWebSearchTool(),
    "retrival_from_database": RetrivalFromDatabaseTool(),
    "jina_search": JinaSearchTool(),
    "jina_read_urls": JinaReadUrlsTool(),
    "youtube_caption": YouTubeCaptionTool(),
    "wechatmp_spider": WechatmpSpiderTool(),
    "paper_with_code_search": PaperWithCodeTool(),
    "finance_news_search": FinanceNewsSearchTool(),
    "browser_use": BrowserUseTool(),
    "vl_model": VLModelTool(),
    "code_execute": CodeExecuteTool(),
    "paper_with_code_search_full": PaperWithCodeFullTool(),
    "send_email": SendEmailTool(),
    "flow_chart": FlowChartTool(),
    "mermaid_add_picture": MermaidAddPictureTool(),
    "pdf2pictures": PDF2PicturesTool(),
    "images_layout_analysis": ImagesLayoutAnalysisTool(),
    "extract_tables_images_from_images": ExtractTablesImagesFromImagesTool(),
    "bilibili_retrieval": BiliBiliRetrievalTool(),
    "pdf_download": PDFDownloadTool(),
    "pdf_reader": PDFReaderTool(),
    "twitter_spider": TwitterSpiderTool(),
    "youtube_retrieval": YouTubeRetrievalTool(),
    "condition_judge": ConditionJudgeTool(),
    "orca_dir_reader": OrcaDirReaderTool(),
    "google_search": GoogleSearchTool()
}

__all__ = ["tools"] 