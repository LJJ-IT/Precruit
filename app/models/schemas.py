"""
Precruit 数据模型

定义所有 Agent 输入/输出、API 请求/响应的 Pydantic 模型。
"""

from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
# Agent 1 输出：文档解析结果
# ═══════════════════════════════════════════════════════════════════

class ParsedResume(BaseModel):
    """简历解析结果"""
    name: str = Field(default="", description="候选人姓名")
    email: str = Field(default="", description="邮箱")
    phone: str = Field(default="", description="手机号")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    experience: list[str] = Field(default_factory=list, description="工作/项目经历")
    education: str = Field(default="", description="教育背景")
    github_username: str = Field(default="", description="GitHub用户名")
    self_intro: str = Field(default="", description="自我评价")
    completeness: int = Field(default=0, description="简历完整度 0-100")


class ParsedJD(BaseModel):
    """JD解析结果"""
    company_name: str = Field(default="", description="公司名称")
    position: str = Field(default="", description="职位名称")
    required_skills: list[str] = Field(default_factory=list, description="技术要求")
    responsibilities: list[str] = Field(default_factory=list, description="工作职责")
    culture_keywords: list[str] = Field(default_factory=list, description="文化关键词（加班/远程/扁平化等）")
    description: str = Field(default="", description="JD原文摘要")


class ParseResult(BaseModel):
    """Agent 1 完整输出"""
    resume: ParsedResume = Field(default_factory=ParsedResume)
    jd: ParsedJD = Field(default_factory=ParsedJD)


# ═══════════════════════════════════════════════════════════════════
# Agent 2 输出：技能与经历匹配
# ═══════════════════════════════════════════════════════════════════

class GitHubEvaluation(BaseModel):
    """GitHub 代码评估（条件输出）"""
    available: bool = Field(default=False, description="是否获取到GitHub数据")
    score: int = Field(default=0, description="GitHub能力评分 0-100")
    top_repos: list[str] = Field(default_factory=list, description="代表性仓库")
    activity_level: str = Field(default="unknown", description="活跃度: high/medium/low")
    summary: str = Field(default="", description="评估总结")


class SkillMatchResult(BaseModel):
    """Agent 2 完整输出"""
    skill_score: int = Field(default=0, description="技能匹配得分 0-100")
    experience_score: int = Field(default=0, description="经历匹配得分 0-100")
    hard_skill_score: int = Field(default=0, description="综合硬实力得分 0-100")
    matched_skills: list[str] = Field(default_factory=list, description="已匹配技能")
    missing_skills: list[str] = Field(default_factory=list, description="缺失技能")
    matched_projects: list[str] = Field(default_factory=list, description="匹配的项目经历")
    github: GitHubEvaluation = Field(default_factory=GitHubEvaluation, description="GitHub评估（如有）")
    strengths: list[str] = Field(default_factory=list, description="硬实力优势")
    gaps: list[str] = Field(default_factory=list, description="硬实力不足")


# ═══════════════════════════════════════════════════════════════════
# Agent 3 输出：文化匹配
# ═══════════════════════════════════════════════════════════════════

class CultureFitResult(BaseModel):
    """Agent 3 完整输出"""
    score: int = Field(default=0, description="文化匹配得分 0-100")
    company_culture: str = Field(default="", description="公司文化画像")
    company_business: str = Field(default="", description="公司主营业务方向")
    candidate_profile: str = Field(default="", description="候选人软性素质描述")
    match_points: list[str] = Field(default_factory=list, description="文化匹配点")
    risk_points: list[str] = Field(default_factory=list, description="文化风险点")


# ═══════════════════════════════════════════════════════════════════
# Agent 4 输出：综合评分与优化
# ═══════════════════════════════════════════════════════════════════

class FinalReport(BaseModel):
    """Agent 4 最终报告"""
    candidate_name: str = Field(default="", description="候选人姓名")
    candidate_email: str = Field(default="", description="候选人邮箱")
    position: str = Field(default="", description="应聘职位")
    company: str = Field(default="", description="目标公司")

    # 各维度得分
    hard_skill_score: int = Field(default=0, description="硬实力得分 0-100")
    culture_fit_score: int = Field(default=0, description="文化匹配得分 0-100")
    completeness_score: int = Field(default=0, description="简历完整度得分 0-100")
    competitiveness_score: int = Field(default=0, description="综合竞争力得分 0-100")

    # 最终得分
    final_score: float = Field(default=0.0, description="加权最终得分 0-100")
    passed: bool = Field(default=False, description="是否通过（≥阈值）")
    email_sent: bool = Field(default=False, description="是否已发送面试邮件")

    # 详细结果
    hard_skill: SkillMatchResult = Field(default_factory=SkillMatchResult)
    culture_fit: CultureFitResult = Field(default_factory=CultureFitResult)

    # 优化建议
    optimization_suggestions: list[str] = Field(default_factory=list, description="简历优化建议")
    interview_questions: list[str] = Field(default_factory=list, description="建议面试问题")

    # 综合
    overall_summary: str = Field(default="", description="综合评价")
    risk_flags: list[str] = Field(default_factory=list, description="风险标记")


# ═══════════════════════════════════════════════════════════════════
# API 请求 / 响应
# ═══════════════════════════════════════════════════════════════════

class AnalysisRequest(BaseModel):
    """分析请求"""
    resume_text: str = Field(default="", description="简历文本内容")
    jd_text: str = Field(default="", description="JD文本内容", min_length=200)


class AnalysisResponse(BaseModel):
    """分析响应"""
    success: bool = Field(default=True)
    data: Optional[FinalReport] = Field(default=None)
    error: Optional[str] = Field(default=None)
