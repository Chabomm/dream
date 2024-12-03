from typing import Optional, Dict
from pydantic import BaseModel, Field

# include: 반환된 사전에 포함할 필드입니다. 아래 참조
# exclude: 반환된 사전에서 제외할 필드입니다. 아래 참조
# by_alias: 반환된 사전에서 필드 별칭을 키로 사용해야 하는지 여부; 기본False
# exclude_unset: 모델을 생성할 때 명시적으로 설정되지 않은 필드를 반환된 사전에서 제외해야 하는지 여부; 기본값 False. v1.0 이전 에는 ; exclude_unset_ skip_defaults의 사용은 skip_defaults이제 더 이상 사용되지 않습니다
# exclude_defaults: 기본값과 동일한 필드(설정 여부에 관계없이)를 반환된 사전에서 제외해야 하는지 여부; 기본False
# exclude_none: 반환된 사전에서 동일한 필드를 제외해야 하는지 여부 ; 기본 False
class AppModel(BaseModel):
    def dict(self, *args, **kwargs):
        if kwargs and kwargs.get("exclude_none") is not None:
            # kwargs["exclude_unset"] = True
            # kwargs["exclude_defaults"] = True
            kwargs["exclude_none"] = True
        return BaseModel.dict(self, *args, **kwargs)


class Status(AppModel):
    status: int = Field(200, title="코드")
    code: int = Field(200, title="코드")
    msg: str = Field("", title="메시지")

class PPage(AppModel):
    page: int = Field(1, title="현재페이지")
    sort: int = Field(1, title="정렬")

class PPage_param(AppModel):
    page: int = Field(1, title="현재페이지")
    page_size: int = Field(0, title="현재 페이지에 검색된 수")
    page_view_size: int = Field(0, title="한 페이지에 보일 수")
    page_total: int = Field(0, title="전체 게시물 수") 
    page_last: int = Field(0, title="전체 페이지 수") 
    filters: Optional[Dict] = Field(default_factory=dict)
    
class PRead(AppModel):
    uid: int   

class Files(BaseModel) : 
    uid: Optional[int] = Field(0, title="파일 고유번호")
    table_name: Optional[str] = Field("", title="테이블 이름")
    table_uid: Optional[int] = Field(0, title="테이블 고유번호")
    fake_name: Optional[str] = Field(None, title="원본파일명")
    file_name: Optional[str] = Field(None, title="저장된 파일명")
    file_ext: Optional[str] = Field(None, title="파일확장자")
    upload_path: Optional[str] = Field(None, title="파일경로")
    sort: Optional[int] = Field(0, title="파일 순서")