#!/usr/bin/env python3
"""
测试用例匹配器 - 核心匹配逻辑
支持客户用例与内部用例的语义级别匹配
"""

import pandas as pd
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Confidence(Enum):
    """匹配置信度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class MatchResult:
    """匹配结果"""
    customer_case_id: str
    customer_case_name: str
    internal_case_id: str
    internal_case_name: str
    confidence: str
    reason: str
    similarity_score: float


@dataclass
class TestCase:
    """测试用例结构"""
    id: str
    name: str
    steps: str
    precondition: str = ""
    expected_result: str = ""


class CustomerCaseParser:
    """客户用例解析器 - 智能识别用例结构"""

    # 常见的用例名称列关键词
    NAME_KEYWORDS = [
        '用例名称', '测试用例', '用例', 'case name', 'test case',
        '测试项', '功能点', '测试点', '测试内容', '测试场景',
        '用例标题', '测试名称', '用例编号'
    ]

    # 常见的用例步骤列关键词
    STEP_KEYWORDS = [
        '测试步骤', '操作步骤', '步骤', 'step', '测试过程',
        '操作过程', '执行步骤', '测试流程', '操作描述',
        '测试操作', '执行过程', '用例步骤'
    ]

    # 常见的预期结果列关键词
    EXPECTED_KEYWORDS = [
        '预期结果', '期望结果', '预期', 'expected', '期望',
        '预期输出', '预期表现', '期望输出'
    ]

    # 常见的预置条件列关键词
    PRECONDITION_KEYWORDS = [
        '预置条件', '前置条件', '前提条件', 'precondition',
        '前置', '准备条件', '测试前提'
    ]

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.xls = pd.ExcelFile(file_path)
        self.sheet_names = self.xls.sheet_names

    def find_case_sheet(self) -> Tuple[str, pd.DataFrame]:
        """
        智能识别包含测试用例的子表
        返回: (子表名称, DataFrame)
        """
        best_sheet = None
        best_score = 0
        best_df = None

        for sheet_name in self.sheet_names:
            df = pd.read_excel(self.xls, sheet_name=sheet_name)

            # 跳过空表或数据量太少的表
            if df.empty or len(df) < 2:
                continue

            # 计算该表作为用例表的得分
            score = self._calculate_case_sheet_score(df)

            if score > best_score:
                best_score = score
                best_sheet = sheet_name
                best_df = df

        if best_sheet is None:
            raise ValueError("未找到包含测试用例的子表")

        return best_sheet, best_df

    def _calculate_case_sheet_score(self, df: pd.DataFrame) -> int:
        """计算子表作为用例表的可能性得分"""
        score = 0
        columns = [str(col).lower() for col in df.columns]

        # 检查是否包含用例名称列
        for col in columns:
            if any(kw in col for kw in [k.lower() for k in self.NAME_KEYWORDS]):
                score += 10

        # 检查是否包含步骤列
        for col in columns:
            if any(kw in col for kw in [k.lower() for kw in self.STEP_KEYWORDS]):
                score += 15

        # 检查是否包含预期结果列
        for col in columns:
            if any(kw in col for kw in [k.lower() for kw in self.EXPECTED_KEYWORDS]):
                score += 5

        # 检查数据行数（合理的用例数量）
        if 5 <= len(df) <= 500:
            score += 5
        elif len(df) > 500:
            score += 2

        return score

    def identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        识别各列的用途
        返回: {用途: 列名}
        """
        columns = {str(col): col for col in df.columns}
        result = {}

        # 识别名称列
        for col in columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in [k.lower() for k in self.NAME_KEYWORDS]):
                result['name'] = col
                break

        # 如果没找到名称列，选择第一列作为名称
        if 'name' not in result:
            result['name'] = df.columns[0]

        # 识别步骤列
        for col in columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in [k.lower() for kw in self.STEP_KEYWORDS]):
                result['steps'] = col
                break

        # 识别预期结果列
        for col in columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in [k.lower() for kw in self.EXPECTED_KEYWORDS]):
                result['expected'] = col
                break

        # 识别预置条件列
        for col in columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in [k.lower() for kw in self.PRECONDITION_KEYWORDS]):
                result['precondition'] = col
                break

        return result

    def parse_cases(self) -> List[TestCase]:
        """解析所有测试用例"""
        sheet_name, df = self.find_case_sheet()
        columns = self.identify_columns(df)

        cases = []
        for idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row.get(columns.get('name', df.columns[0]))):
                continue

            case = TestCase(
                id=str(idx + 1),
                name=str(row.get(columns.get('name', df.columns[0]), '')),
                steps=str(row.get(columns.get('steps', ''), '')),
                precondition=str(row.get(columns.get('precondition', ''), '')),
                expected_result=str(row.get(columns.get('expected', ''), ''))
            )

            # 只保留有效用例（至少有名称）
            if case.name and case.name != 'nan':
                cases.append(case)

        return cases


class InternalCaseParser:
    """内部用例解析器"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def parse_cases(self) -> List[TestCase]:
        """解析内部测试用例"""
        df = pd.read_excel(self.file_path)

        cases = []
        for idx, row in df.iterrows():
            # 跳过空行
            if pd.isna(row.get('用例_名称')):
                continue

            case = TestCase(
                id=str(idx + 1),
                name=str(row.get('用例_名称', '')),
                steps=str(row.get('用例_测试步骤', '')),
                precondition=str(row.get('用例_预置条件', '')),
                expected_result=str(row.get('用例_预期结果', ''))
            )

            if case.name and case.name != 'nan':
                cases.append(case)

        return cases


class SemanticMatcher:
    """语义匹配器"""

    def __init__(self):
        # 停用词
        self.stop_words = {'的', '了', '在', '是', '有', '和', '与', '或', '等', '中', '为', '以', '及'}

    def match(self, customer_cases: List[TestCase], internal_cases: List[TestCase]) -> List[MatchResult]:
        """
        执行匹配
        返回所有匹配结果（多对多）
        """
        results = []

        for cc in customer_cases:
            for ic in internal_cases:
                match = self._match_pair(cc, ic)
                if match:
                    results.append(match)

        return results

    def _match_pair(self, customer_case: TestCase, internal_case: TestCase) -> Optional[MatchResult]:
        """匹配一对用例"""
        # 计算步骤相似度
        step_similarity = self._calculate_similarity(
            customer_case.steps,
            internal_case.steps
        )

        # 计算名称相似度（作为辅助）
        name_similarity = self._calculate_similarity(
            customer_case.name,
            internal_case.name
        )

        # 综合相似度（步骤权重更高）
        total_similarity = step_similarity * 0.7 + name_similarity * 0.3

        # 判断是否匹配
        if total_similarity < 0.2:
            return None

        # 确定置信度
        if total_similarity >= 0.6:
            confidence = Confidence.HIGH
        elif total_similarity >= 0.4:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        # 生成匹配理由
        reason = self._generate_reason(customer_case, internal_case, step_similarity, name_similarity)

        return MatchResult(
            customer_case_id=customer_case.id,
            customer_case_name=customer_case.name,
            internal_case_id=internal_case.id,
            internal_case_name=internal_case.name,
            confidence=confidence.value,
            reason=reason,
            similarity_score=round(total_similarity, 3)
        )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度
        使用关键词重叠 + Jaccard 相似度
        """
        if not text1 or not text2 or text1 == 'nan' or text2 == 'nan':
            return 0.0

        # 提取关键词
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)

        if not keywords1 or not keywords2:
            return 0.0

        # Jaccard 相似度
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0

    def _extract_keywords(self, text: str) -> set:
        """提取关键词"""
        # 简单分词（按空格、标点分割）
        words = re.split(r'[\s,，。.!！?？;；:：、]+', text)

        # 过滤停用词和短词
        keywords = {
            w.lower() for w in words
            if len(w) >= 2 and w.lower() not in self.stop_words
        }

        return keywords

    def _generate_reason(self, cc: TestCase, ic: TestCase,
                         step_sim: float, name_sim: float) -> str:
        """生成匹配理由"""
        reasons = []

        if step_sim >= 0.5:
            reasons.append("测试步骤高度相似")
        elif step_sim >= 0.3:
            reasons.append("测试步骤部分相似")

        if name_sim >= 0.5:
            reasons.append("用例名称相关")

        if not reasons:
            reasons.append("存在语义关联")

        return "；".join(reasons)


class ReportGenerator:
    """报告生成器"""

    def generate_excel(self, results: List[MatchResult],
                       customer_cases: List[TestCase],
                       internal_cases: List[TestCase],
                       output_path: str):
        """生成 Excel 报告"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 匹配汇总表
            match_df = pd.DataFrame([asdict(r) for r in results])
            if not match_df.empty:
                match_df.to_excel(writer, sheet_name='匹配汇总', index=False)

            # 客户用例视角
            customer_view = self._build_customer_view(results, customer_cases)
            customer_view.to_excel(writer, sheet_name='客户用例视角', index=False)

            # 内部用例视角
            internal_view = self._build_internal_view(results, internal_cases)
            internal_view.to_excel(writer, sheet_name='内部用例视角', index=False)

            # 统计信息
            stats = self._build_statistics(results, customer_cases, internal_cases)
            stats.to_excel(writer, sheet_name='统计信息', index=False)

    def generate_markdown(self, results: List[MatchResult],
                          customer_cases: List[TestCase],
                          internal_cases: List[TestCase]) -> str:
        """生成 Markdown 报告"""
        md = ["# 测试用例匹配报告\n"]

        # 统计信息
        stats = self._build_statistics(results, customer_cases, internal_cases)
        md.append("## 统计信息\n")
        md.append(stats.to_markdown(index=False))
        md.append("\n")

        # 匹配汇总
        md.append("## 匹配汇总\n")
        if results:
            match_df = pd.DataFrame([{
                '客户用例': r.customer_case_name,
                '内部用例': r.internal_case_name,
                '置信度': r.confidence,
                '匹配理由': r.reason
            } for r in results])
            md.append(match_df.to_markdown(index=False))
        else:
            md.append("无匹配结果")
        md.append("\n")

        # 未匹配项
        matched_customer = {r.customer_case_id for r in results}
        matched_internal = {r.internal_case_id for r in results}

        unmatched_customer = [c for c in customer_cases if c.id not in matched_customer]
        unmatched_internal = [c for c in internal_cases if c.id not in matched_internal]

        if unmatched_customer:
            md.append("## 客户用例（未找到匹配）\n")
            for c in unmatched_customer:
                md.append(f"- {c.name}\n")
            md.append("\n")

        if unmatched_internal:
            md.append("## 内部用例（未被覆盖）\n")
            for c in unmatched_internal:
                md.append(f"- {c.name}\n")
            md.append("\n")

        return "".join(md)

    def _build_customer_view(self, results: List[MatchResult],
                              customer_cases: List[TestCase]) -> pd.DataFrame:
        """构建客户用例视角视图"""
        view_data = {}
        for c in customer_cases:
            view_data[c.id] = {
                '客户用例ID': c.id,
                '客户用例名称': c.name,
                '匹配的内部用例': [],
                '最高置信度': ''
            }

        for r in results:
            if r.customer_case_id in view_data:
                view_data[r.customer_case_id]['匹配的内部用例'].append(
                    f"{r.internal_case_name}({r.confidence})"
                )

        for vid in view_data:
            matches = view_data[vid]['匹配的内部用例']
            view_data[vid]['匹配的内部用例'] = '; '.join(matches) if matches else '无匹配'
            # 确定最高置信度
            if any('高' in m for m in matches):
                view_data[vid]['最高置信度'] = '高'
            elif any('中' in m for m in matches):
                view_data[vid]['最高置信度'] = '中'
            elif matches:
                view_data[vid]['最高置信度'] = '低'
            else:
                view_data[vid]['最高置信度'] = '无'

        return pd.DataFrame(list(view_data.values()))

    def _build_internal_view(self, results: List[MatchResult],
                              internal_cases: List[TestCase]) -> pd.DataFrame:
        """构建内部用例视角视图"""
        view_data = {}
        for c in internal_cases:
            view_data[c.id] = {
                '内部用例ID': c.id,
                '内部用例名称': c.name,
                '对应的客户用例': [],
                '最高置信度': ''
            }

        for r in results:
            if r.internal_case_id in view_data:
                view_data[r.internal_case_id]['对应的客户用例'].append(
                    f"{r.customer_case_name}({r.confidence})"
                )

        for vid in view_data:
            matches = view_data[vid]['对应的客户用例']
            view_data[vid]['对应的客户用例'] = '; '.join(matches) if matches else '未被覆盖'
            if any('高' in m for m in matches):
                view_data[vid]['最高置信度'] = '高'
            elif any('中' in m for m in matches):
                view_data[vid]['最高置信度'] = '中'
            elif matches:
                view_data[vid]['最高置信度'] = '低'
            else:
                view_data[vid]['最高置信度'] = '无'

        return pd.DataFrame(list(view_data.values()))

    def _build_statistics(self, results: List[MatchResult],
                           customer_cases: List[TestCase],
                           internal_cases: List[TestCase]) -> pd.DataFrame:
        """构建统计信息"""
        total_customer = len(customer_cases)
        total_internal = len(internal_cases)
        matched_customer = len({r.customer_case_id for r in results})
        matched_internal = len({r.internal_case_id for r in results})

        high_count = len([r for r in results if r.confidence == '高'])
        medium_count = len([r for r in results if r.confidence == '中'])
        low_count = len([r for r in results if r.confidence == '低'])

        return pd.DataFrame([
            {'指标': '客户用例总数', '数值': total_customer},
            {'指标': '内部用例总数', '数值': total_internal},
            {'指标': '已匹配客户用例数', '数值': matched_customer},
            {'指标': '已匹配内部用例数', '数值': matched_internal},
            {'指标': '客户用例匹配率', '数值': f"{matched_customer/total_customer*100:.1f}%" if total_customer > 0 else "0%"},
            {'指标': '内部用例覆盖率', '数值': f"{matched_internal/total_internal*100:.1f}%" if total_internal > 0 else "0%"},
            {'指标': '高置信度匹配数', '数值': high_count},
            {'指标': '中置信度匹配数', '数值': medium_count},
            {'指标': '低置信度匹配数', '数值': low_count},
        ])


def main():
    """主函数 - 供 agent 调用"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python matcher.py <客户用例文件> <内部用例文件> [输出格式: excel/markdown]")
        sys.exit(1)

    customer_file = sys.argv[1]
    internal_file = sys.argv[2]
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'excel'

    print(f"解析客户用例文件: {customer_file}")
    customer_parser = CustomerCaseParser(customer_file)
    customer_cases = customer_parser.parse_cases()
    print(f"找到 {len(customer_cases)} 条客户用例")

    print(f"解析内部用例文件: {internal_file}")
    internal_parser = InternalCaseParser(internal_file)
    internal_cases = internal_parser.parse_cases()
    print(f"找到 {len(internal_cases)} 条内部用例")

    print("执行语义匹配...")
    matcher = SemanticMatcher()
    results = matcher.match(customer_cases, internal_cases)
    print(f"找到 {len(results)} 个匹配关系")

    # 生成报告
    report_gen = ReportGenerator()

    if output_format == 'markdown':
        report = report_gen.generate_markdown(results, customer_cases, internal_cases)
        output_file = "testcase_match_report.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
    else:
        output_file = "testcase_match_report.xlsx"
        report_gen.generate_excel(results, customer_cases, internal_cases, output_file)

    print(f"报告已生成: {output_file}")
    return output_file


if __name__ == "__main__":
    main()
