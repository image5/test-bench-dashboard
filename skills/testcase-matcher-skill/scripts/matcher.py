#!/usr/bin/env python3
"""
测试用例匹配器 - 核心匹配逻辑
根据用户指定的列，比对客户用例和内部用例的测试步骤
"""

import pandas as pd
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class MatchLevel(Enum):
    """匹配程度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    steps: str
    row_num: int


@dataclass
class MatchResult:
    """匹配结果"""
    customer_case_name: str
    customer_case_id: str
    internal_case_name: str
    internal_case_id: str
    match_level: str
    match_reason: str
    similarity_score: float


def read_excel_column(df: pd.DataFrame, col_spec: str) -> pd.Series:
    """
    根据列规格读取列数据
    支持：列字母(A,B,C)、列名、列序号(1,2,3)
    """
    col_spec = str(col_spec).strip()
    
    # 尝试作为列字母解析 (A=0, B=1, ...)
    if col_spec.isalpha() and len(col_spec) <= 3:
        col_index = 0
        for char in col_spec.upper():
            col_index = col_index * 26 + (ord(char) - ord('A') + 1)
        col_index -= 1  # 转为0-based索引
        if 0 <= col_index < len(df.columns):
            return df.iloc[:, col_index]
    
    # 尝试作为列序号解析
    if col_spec.isdigit():
        col_index = int(col_spec) - 1  # 转为0-based索引
        if 0 <= col_index < len(df.columns):
            return df.iloc[:, col_index]
    
    # 尝试作为列名匹配
    for col in df.columns:
        if col_spec in str(col):
            return df[col]
    
    raise ValueError(f"无法找到列: {col_spec}")


def load_cases(file_path: str, sheet_name: str, name_col: str, steps_col: str) -> List[TestCase]:
    """加载测试用例"""
    xls = pd.ExcelFile(file_path)
    
    # 如果没有指定子表，使用第一个
    if not sheet_name:
        sheet_name = xls.sheet_names[0]
    
    df = pd.read_excel(xls, sheet_name=sheet_name)
    
    # 读取名称列和步骤列
    name_series = read_excel_column(df, name_col)
    steps_series = read_excel_column(df, steps_col)
    
    cases = []
    for idx, (name, steps) in enumerate(zip(name_series, steps_series)):
        # 跳过空行
        if pd.isna(name) or str(name).strip() == '':
            continue
        
        case = TestCase(
            id=str(idx + 1),
            name=str(name).strip(),
            steps=str(steps) if not pd.isna(steps) else "",
            row_num=idx + 2  # Excel行号（从2开始，因为第1行是表头）
        )
        cases.append(case)
    
    return cases


def extract_keywords(text: str) -> set:
    """提取关键词"""
    if not text or text == 'nan':
        return set()
    
    # 停用词
    stop_words = {'的', '了', '在', '是', '有', '和', '与', '或', '等', '中', '为', '以', '及', '到', '对', '将'}
    
    # 分词（按空格、标点分割）
    words = re.split(r'[\s,，。.!！?？;；:：、\n\r\t]+', text)
    
    # 过滤
    keywords = {
        w.lower() for w in words
        if len(w) >= 2 and w.lower() not in stop_words
    }
    
    return keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（Jaccard相似度）"""
    kw1 = extract_keywords(text1)
    kw2 = extract_keywords(text2)
    
    if not kw1 or not kw2:
        return 0.0
    
    intersection = len(kw1 & kw2)
    union = len(kw1 | kw2)
    
    return intersection / union if union > 0 else 0.0


def match_cases(customer_cases: List[TestCase], internal_cases: List[TestCase]) -> List[MatchResult]:
    """匹配用例"""
    results = []
    
    for cc in customer_cases:
        for ic in internal_cases:
            # 计算步骤相似度
            similarity = calculate_similarity(cc.steps, ic.steps)
            
            # 过滤低相似度
            if similarity < 0.15:
                continue
            
            # 确定匹配程度
            if similarity >= 0.5:
                level = MatchLevel.HIGH
            elif similarity >= 0.3:
                level = MatchLevel.MEDIUM
            else:
                level = MatchLevel.LOW
            
            # 生成匹配说明
            reason = generate_match_reason(cc.steps, ic.steps, similarity)
            
            results.append(MatchResult(
                customer_case_name=cc.name,
                customer_case_id=cc.id,
                internal_case_name=ic.name,
                internal_case_id=ic.id,
                match_level=level.value,
                match_reason=reason,
                similarity_score=round(similarity, 3)
            ))
    
    return results


def generate_match_reason(steps1: str, steps2: str, similarity: float) -> str:
    """生成匹配说明"""
    kw1 = extract_keywords(steps1)
    kw2 = extract_keywords(steps2)
    common = kw1 & kw2
    
    if similarity >= 0.5:
        return f"步骤高度相似，共同关键词：{', '.join(list(common)[:5])}"
    elif similarity >= 0.3:
        return f"步骤部分相似，共同关键词：{', '.join(list(common)[:3])}"
    else:
        return f"存在语义关联，共同关键词：{', '.join(list(common)[:2])}"


def generate_report(results: List[MatchResult], 
                    customer_cases: List[TestCase],
                    internal_cases: List[TestCase],
                    output_path: str):
    """生成Excel报告"""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # 1. 匹配结果表（客户视角）
        customer_view = {}
        for cc in customer_cases:
            customer_view[cc.id] = {
                '序号': len(customer_view) + 1,
                '客户用例名称': cc.name,
                '匹配的内部用例': [],
                '匹配程度': '',
                '匹配说明': ''
            }
        
        for r in results:
            if r.customer_case_id in customer_view:
                customer_view[r.customer_case_id]['匹配的内部用例'].append(
                    f"{r.internal_case_name}({r.match_level})"
                )
        
        # 确定每个客户用例的最高匹配程度
        for vid, vdata in customer_view.items():
            matches = vdata['匹配的内部用例']
            vdata['匹配的内部用例'] = '; '.join(matches) if matches else '无匹配'
            if any('高' in m for m in matches):
                vdata['匹配程度'] = '高'
            elif any('中' in m for m in matches):
                vdata['匹配程度'] = '中'
            elif matches:
                vdata['匹配程度'] = '低'
            else:
                vdata['匹配程度'] = '无匹配'
        
        df_customer = pd.DataFrame(list(customer_view.values()))
        df_customer.to_excel(writer, sheet_name='匹配结果', index=False)
        
        # 2. 内部用例覆盖表（内部视角）
        internal_view = {}
        for ic in internal_cases:
            internal_view[ic.id] = {
                '序号': len(internal_view) + 1,
                '内部用例名称': ic.name,
                '对应的客户用例': [],
                '覆盖程度': ''
            }
        
        for r in results:
            if r.internal_case_id in internal_view:
                internal_view[r.internal_case_id]['对应的客户用例'].append(
                    f"{r.customer_case_name}({r.match_level})"
                )
        
        for vid, vdata in internal_view.items():
            matches = vdata['对应的客户用例']
            vdata['对应的客户用例'] = '; '.join(matches) if matches else '未被覆盖'
            if any('高' in m for m in matches):
                vdata['覆盖程度'] = '高'
            elif any('中' in m for m in matches):
                vdata['覆盖程度'] = '中'
            elif matches:
                vdata['覆盖程度'] = '低'
            else:
                vdata['覆盖程度'] = '无'
        
        df_internal = pd.DataFrame(list(internal_view.values()))
        df_internal.to_excel(writer, sheet_name='内部用例覆盖', index=False)
        
        # 3. 未匹配项
        matched_customer = {r.customer_case_id for r in results}
        matched_internal = {r.internal_case_id for r in results}
        
        unmatched_customer = [c for c in customer_cases if c.id not in matched_customer]
        unmatched_internal = [c for c in internal_cases if c.id not in matched_internal]
        
        df_unmatched = pd.DataFrame({
            '类型': ['客户用例（未找到匹配）'] * len(unmatched_customer) + 
                   ['内部用例（未被覆盖）'] * len(unmatched_internal),
            '用例名称': [c.name for c in unmatched_customer] + [c.name for c in unmatched_internal]
        })
        df_unmatched.to_excel(writer, sheet_name='未匹配项', index=False)
        
        # 4. 统计信息
        total_customer = len(customer_cases)
        total_internal = len(internal_cases)
        matched_customer_count = len(matched_customer)
        matched_internal_count = len(matched_internal)
        
        high_count = len([r for r in results if r.match_level == '高'])
        medium_count = len([r for r in results if r.match_level == '中'])
        low_count = len([r for r in results if r.match_level == '低'])
        
        df_stats = pd.DataFrame([
            {'指标': '客户用例总数', '数值': total_customer},
            {'指标': '内部用例总数', '数值': total_internal},
            {'指标': '已匹配客户用例数', '数值': matched_customer_count},
            {'指标': '已匹配内部用例数', '数值': matched_internal_count},
            {'指标': '客户用例匹配率', '数值': f"{matched_customer_count/total_customer*100:.1f}%" if total_customer > 0 else "0%"},
            {'指标': '内部用例覆盖率', '数值': f"{matched_internal_count/total_internal*100:.1f}%" if total_internal > 0 else "0%"},
            {'指标': '高度匹配数', '数值': high_count},
            {'指标': '中度匹配数', '数值': medium_count},
            {'指标': '低度匹配数', '数值': low_count},
            {'指标': '生成时间', '数值': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ])
        df_stats.to_excel(writer, sheet_name='统计信息', index=False)
        
        # 5. 详细匹配记录
        df_detail = pd.DataFrame([asdict(r) for r in results])
        if not df_detail.empty:
            df_detail = df_detail[['customer_case_name', 'internal_case_name', 'match_level', 'match_reason', 'similarity_score']]
            df_detail.columns = ['客户用例', '内部用例', '匹配程度', '匹配说明', '相似度']
            df_detail.to_excel(writer, sheet_name='详细匹配记录', index=False)


def main():
    """主函数"""
    if len(sys.argv) < 9:
        print("用法: python matcher.py <客户文件> <客户子表> <客户名称列> <客户步骤列> <内部文件> <内部子表> <内部名称列> <内部步骤列> [输出文件]")
        print("\n示例:")
        print("  python matcher.py 客户用例.xlsx 测试用例 B D 内部用例.xlsx Sheet1 A C 匹配报告.xlsx")
        sys.exit(1)
    
    customer_file = sys.argv[1]
    customer_sheet = sys.argv[2]
    customer_name_col = sys.argv[3]
    customer_steps_col = sys.argv[4]
    
    internal_file = sys.argv[5]
    internal_sheet = sys.argv[6]
    internal_name_col = sys.argv[7]
    internal_steps_col = sys.argv[8]
    
    output_file = sys.argv[9] if len(sys.argv) > 9 else "匹配报告.xlsx"
    
    print(f"读取客户用例: {customer_file} (子表: {customer_sheet or '第一个'})")
    customer_cases = load_cases(customer_file, customer_sheet, customer_name_col, customer_steps_col)
    print(f"  找到 {len(customer_cases)} 条客户用例")
    
    print(f"读取内部用例: {internal_file} (子表: {internal_sheet or '第一个'})")
    internal_cases = load_cases(internal_file, internal_sheet, internal_name_col, internal_steps_col)
    print(f"  找到 {len(internal_cases)} 条内部用例")
    
    print("执行步骤比对...")
    results = match_cases(customer_cases, internal_cases)
    print(f"  找到 {len(results)} 个匹配关系")
    
    print(f"生成报告: {output_file}")
    generate_report(results, customer_cases, internal_cases, output_file)
    
    # 输出统计
    matched_customer = len({r.customer_case_id for r in results})
    high_count = len([r for r in results if r.match_level == '高'])
    medium_count = len([r for r in results if r.match_level == '中'])
    low_count = len([r for r in results if r.match_level == '低'])
    
    print("\n=== 匹配统计 ===")
    print(f"客户用例匹配率: {matched_customer}/{len(customer_cases)} ({matched_customer/len(customer_cases)*100:.1f}%)")
    print(f"高度匹配: {high_count}")
    print(f"中度匹配: {medium_count}")
    print(f"低度匹配: {low_count}")
    print(f"\n报告已保存: {output_file}")
    
    return output_file


if __name__ == "__main__":
    main()
