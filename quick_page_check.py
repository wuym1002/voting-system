#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速页码核对工具
"""

import os
import subprocess

def quick_check():
    """
    快速检查关键页码
    """
    print("🔍 快速页码核对")
    print("=" * 50)
    
    # 检查几个关键文件
    key_files = [
        ("P5-1.png", "当前标记为第5页"),
        ("P9-1.png", "当前标记为第9页"), 
        ("P10-1.png", "当前标记为第10页"),
        ("P188-1.png", "当前标记为第188页")
    ]
    
    for filename, description in key_files:
        filepath = os.path.join("media", filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"\n📷 {filename}")
            print(f"   {description}")
            print(f"   大小: {size:.1f} KB")
            
            # 询问是否查看
            view = input(f"   是否查看此图片？(y/N): ").strip().lower()
            if view == 'y':
                try:
                    subprocess.run(['open', '-a', 'Preview', filepath], 
                                 capture_output=True, timeout=3)
                    print(f"   ✅ 已在Preview中打开")
                    
                    # 询问页码是否正确
                    correct = input(f"   这张图片的页码是否正确？(y/n/skip): ").strip().lower()
                    if correct == 'n':
                        new_page = input(f"   请输入正确的页码: ").strip()
                        if new_page.isdigit():
                            print(f"   📝 记录：{filename} 应该是 P{new_page}-1")
                        else:
                            print(f"   ⚠️  页码输入无效")
                    elif correct == 'y':
                        print(f"   ✅ 页码正确")
                    else:
                        print(f"   ⏭️  跳过")
                        
                except Exception as e:
                    print(f"   ❌ 无法打开图片: {e}")
        else:
            print(f"\n❌ {filename} 不存在")
    
    print(f"\n💡 建议的核对流程:")
    print(f"1. 打开Word文档")
    print(f"2. 逐页查看，找到有图片的页面")
    print(f"3. 记录每张图片对应的真实页码")
    print(f"4. 使用批量重命名工具修正")

def show_current_distribution():
    """
    显示当前页码分布
    """
    files = []
    for file in os.listdir("media"):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            files.append(file)
    
    # 提取页码
    pages = []
    for file in files:
        if file.startswith('P'):
            try:
                page_num = int(file[1:].split('-')[0])
                pages.append(page_num)
            except:
                pass
    
    pages.sort()
    
    print(f"📊 当前页码分布:")
    print(f"   总图片数: {len(files)}")
    print(f"   页码范围: P{min(pages)} - P{max(pages)}")
    print(f"   前10个页码: {pages[:10]}")
    print(f"   后10个页码: {pages[-10:]}")
    
    # 检查可能的问题
    print(f"\n⚠️  可能的问题:")
    if min(pages) > 1:
        print(f"   - 缺少第1页图片")
    
    gaps = []
    for i in range(1, len(pages)):
        gap = pages[i] - pages[i-1]
        if gap > 10:
            gaps.append((pages[i-1], pages[i], gap))
    
    if gaps:
        print(f"   - 发现大间隔:")
        for start, end, gap in gaps[:3]:
            print(f"     P{start} → P{end} (间隔{gap}页)")

def main():
    print("🎯 页码核对助手")
    print("帮助您快速核对关键页码是否正确")
    print()
    
    # 显示当前分布
    show_current_distribution()
    
    print(f"\n" + "=" * 50)
    
    # 快速检查
    check = input("是否进行快速页码检查？(Y/n): ").strip().lower()
    if check != 'n':
        quick_check()
    
    print(f"\n🔧 如需批量修正，请运行:")
    print(f"   python3 page_verification_tool.py")

if __name__ == "__main__":
    main()