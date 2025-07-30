#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成图片页码检查报告
"""

import os

def generate_report():
    """
    生成详细的页码分布报告
    """
    media_dir = "media"
    if not os.path.exists(media_dir):
        print("错误：media文件夹不存在")
        return
    
    # 获取所有图片文件
    files = []
    for file in os.listdir(media_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            files.append(file)
    
    # 按页码排序
    def extract_page_num(filename):
        try:
            if filename.startswith('P'):
                page_part = filename[1:].split('-')[0]
                return int(page_part)
            return 0
        except:
            return 0
    
    files.sort(key=extract_page_num)
    
    print("=" * 80)
    print("📊 图片页码整体检查报告")
    print("=" * 80)
    
    print(f"📁 总文件数: {len(files)} 张图片")
    print(f"📄 文档总页数: 305 页 (根据之前分析)")
    print(f"📈 平均分布: 每 {305/len(files):.1f} 页有1张图片")
    
    # 分析页码分布
    pages = []
    for file in files:
        page_num = extract_page_num(file)
        if page_num > 0:
            pages.append(page_num)
    
    if pages:
        print(f"📊 页码范围: P{min(pages)} - P{max(pages)}")
        
        # 检查页码间隔
        gaps = []
        for i in range(1, len(pages)):
            gap = pages[i] - pages[i-1]
            gaps.append(gap)
        
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            print(f"📏 平均页码间隔: {avg_gap:.1f} 页")
            print(f"📏 最小间隔: {min(gaps)} 页")
            print(f"📏 最大间隔: {max(gaps)} 页")
    
    print("\n" + "=" * 80)
    print("🔍 详细页码列表")
    print("=" * 80)
    
    # 按列显示，每行5个
    for i in range(0, len(files), 5):
        row_files = files[i:i+5]
        row_pages = [f"P{extract_page_num(f)}" for f in row_files]
        print(f"{i+1:2d}-{min(i+5, len(files)):2d}: " + "  ".join(f"{p:>6}" for p in row_pages))
    
    print("\n" + "=" * 80)
    print("⚠️  可能存在的问题")
    print("=" * 80)
    
    # 检查可能的问题
    issues = []
    
    # 1. 检查是否缺少P1
    if 1 not in pages:
        issues.append("❌ 缺少第1页 (P1-1)")
    
    # 2. 检查页码跳跃过大的情况
    large_gaps = [(i, pages[i] - pages[i-1]) for i in range(1, len(pages)) if pages[i] - pages[i-1] > 20]
    if large_gaps:
        issues.append(f"⚠️  发现 {len(large_gaps)} 个大间隔 (>20页):")
        for i, gap in large_gaps[:5]:  # 只显示前5个
            issues.append(f"   P{pages[i-1]} → P{pages[i]} (间隔{gap}页)")
    
    # 3. 检查关键页码
    key_pages = [1, 10, 50, 100, 150, 188, 200, 250, 300]
    missing_key_pages = [p for p in key_pages if p not in pages and p <= 305]
    if missing_key_pages:
        issues.append(f"⚠️  缺少关键页码: {missing_key_pages}")
    
    # 4. 检查是否有重复页码
    page_counts = {}
    for page in pages:
        page_counts[page] = page_counts.get(page, 0) + 1
    
    duplicates = [p for p, count in page_counts.items() if count > 1]
    if duplicates:
        issues.append(f"❌ 发现重复页码: {duplicates}")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ 未发现明显问题")
    
    print("\n" + "=" * 80)
    print("💡 建议")
    print("=" * 80)
    
    suggestions = []
    
    if 1 not in pages:
        suggestions.append("📝 建议添加第1页图片 (P1-1)")
    
    if 188 in pages:
        suggestions.append("✅ 第188页图片存在")
    else:
        suggestions.append("❌ 需要确认第188页图片")
    
    # 检查前几页的分布
    early_pages = [p for p in pages if p <= 20]
    if len(early_pages) < 3:
        suggestions.append("📝 建议在前20页增加更多图片")
    
    # 检查页码是否过于稀疏
    if len(pages) > 0 and max(pages) / len(pages) > 10:
        suggestions.append("📝 考虑重新分布图片，使页码更连续")
    
    for suggestion in suggestions:
        print(suggestion)
    
    print("\n" + "=" * 80)
    print("🎯 快速修正建议")
    print("=" * 80)
    
    print("如需修正页码，建议的操作:")
    print("1. 运行交互式工具: python3 interactive_page_corrector.py")
    print("2. 或手动重命名关键文件:")
    
    # 建议一些具体的重命名
    if 1 not in pages and len(pages) > 0:
        first_file = files[0]
        print(f"   mv media/{first_file} media/P1-1.png")
    
    print(f"3. 确保第188页图片正确:")
    p188_files = [f for f in files if f.startswith('P188-')]
    if p188_files:
        print(f"   ✅ 已存在: {p188_files[0]}")
    else:
        print(f"   ❌ 需要指定哪张图片是第188页")

def main():
    generate_report()

if __name__ == "__main__":
    main()