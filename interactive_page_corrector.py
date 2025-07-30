#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式图片页码修正工具
让用户逐一确认每张图片的正确页码
"""

import os
import shutil
from pathlib import Path
import subprocess
import sys

def get_current_files():
    """
    获取当前所有图片文件，按页码排序
    """
    media_dir = "media"
    if not os.path.exists(media_dir):
        print("错误：media文件夹不存在")
        return []
    
    files = []
    for file in os.listdir(media_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            files.append(file)
    
    # 按照页码数字排序
    def extract_page_num(filename):
        try:
            if filename.startswith('P'):
                page_part = filename[1:].split('-')[0]
                return int(page_part)
            return 0
        except:
            return 0
    
    files.sort(key=extract_page_num)
    return files

def show_image_info(filename):
    """
    显示图片信息
    """
    filepath = os.path.join("media", filename)
    if os.path.exists(filepath):
        # 获取文件大小
        size = os.path.getsize(filepath)
        size_kb = size / 1024
        
        print(f"📷 图片信息:")
        print(f"   文件名: {filename}")
        print(f"   大小: {size_kb:.1f} KB")
        print(f"   路径: {filepath}")
        
        # 尝试在系统中打开图片预览（仅macOS）
        try:
            print(f"   正在打开图片预览...")
            subprocess.run(['open', '-a', 'Preview', filepath], 
                          check=False, capture_output=True)
            return True
        except:
            print(f"   无法自动打开图片预览")
            return False
    return False

def get_user_input(current_filename, current_page, index, total):
    """
    获取用户输入的正确页码
    """
    print(f"\n{'='*60}")
    print(f"图片 {index + 1}/{total}: {current_filename}")
    print(f"当前页码: P{current_page}")
    print(f"{'='*60}")
    
    # 显示图片信息
    show_image_info(current_filename)
    
    print(f"\n请选择操作:")
    print(f"1. 输入正确的页码 (只输入数字，如: 25)")
    print(f"2. 保持当前页码 P{current_page} (按回车)")
    print(f"3. 跳过这张图片 (输入 skip)")
    print(f"4. 完成修正并退出 (输入 done)")
    print(f"5. 取消所有修改 (输入 cancel)")
    
    while True:
        user_input = input(f"\n请输入选择: ").strip()
        
        if user_input == "":
            # 保持当前页码
            return current_page, "keep"
        elif user_input.lower() == "skip":
            return current_page, "skip"
        elif user_input.lower() == "done":
            return current_page, "done"
        elif user_input.lower() == "cancel":
            return current_page, "cancel"
        elif user_input.isdigit():
            new_page = int(user_input)
            if 1 <= new_page <= 1000:  # 合理的页码范围
                return new_page, "change"
            else:
                print("❌ 页码应该在1-1000之间，请重新输入")
        else:
            print("❌ 无效输入，请重新选择")

def interactive_correction():
    """
    交互式修正过程
    """
    files = get_current_files()
    if not files:
        print("没有找到图片文件")
        return
    
    print(f"🎯 交互式图片页码修正工具")
    print(f"📊 找到 {len(files)} 张图片需要检查")
    print(f"💡 提示：工具会逐一显示图片，您可以确认或修改页码")
    
    # 创建备份
    backup_dir = "media_backup_interactive"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree("media", backup_dir)
    print(f"✅ 已创建备份到 {backup_dir}")
    
    # 存储修改计划
    corrections = []
    
    for i, filename in enumerate(files):
        try:
            # 提取当前页码
            if filename.startswith('P'):
                current_page_str = filename[1:].split('-')[0]
                current_page = int(current_page_str)
            else:
                current_page = 1
            
            # 获取用户输入
            new_page, action = get_user_input(filename, current_page, i, len(files))
            
            if action == "cancel":
                print(f"\n❌ 用户取消修改")
                return
            elif action == "done":
                print(f"\n✅ 用户选择完成修正")
                break
            elif action == "skip":
                print(f"⏭️  跳过 {filename}")
                continue
            elif action == "change":
                corrections.append((filename, current_page, new_page))
                print(f"📝 计划修改: {filename} → P{new_page}-1")
            elif action == "keep":
                print(f"✅ 保持 {filename} 不变")
            
        except KeyboardInterrupt:
            print(f"\n\n❌ 用户中断操作")
            return
        except Exception as e:
            print(f"❌ 处理 {filename} 时出错: {e}")
            continue
    
    # 应用修改
    if corrections:
        apply_corrections(corrections)
    else:
        print(f"\n📋 没有需要修改的图片")

def apply_corrections(corrections):
    """
    应用页码修正
    """
    print(f"\n🔧 开始应用修正...")
    print(f"📋 计划修改 {len(corrections)} 张图片:")
    
    for old_filename, old_page, new_page in corrections:
        print(f"   {old_filename} → P{new_page}-1")
    
    confirm = input(f"\n确认应用这些修改吗？(y/N): ").strip().lower()
    if confirm != 'y':
        print(f"❌ 用户取消应用修改")
        return
    
    # 执行重命名
    success_count = 0
    error_count = 0
    
    # 先重命名到临时文件，避免命名冲突
    temp_files = []
    
    for old_filename, old_page, new_page in corrections:
        try:
            old_path = os.path.join("media", old_filename)
            if not os.path.exists(old_path):
                print(f"❌ 文件不存在: {old_filename}")
                error_count += 1
                continue
            
            # 获取扩展名
            _, ext = os.path.splitext(old_filename)
            
            # 临时文件名
            temp_filename = f"TEMP_{success_count}_{new_page}-1{ext}"
            temp_path = os.path.join("media", temp_filename)
            
            # 重命名到临时文件
            os.rename(old_path, temp_path)
            temp_files.append((temp_filename, f"P{new_page}-1{ext}"))
            
        except Exception as e:
            print(f"❌ 重命名失败 {old_filename}: {e}")
            error_count += 1
    
    # 从临时文件重命名到最终文件名
    for temp_filename, final_filename in temp_files:
        try:
            temp_path = os.path.join("media", temp_filename)
            final_path = os.path.join("media", final_filename)
            
            # 检查目标文件是否已存在
            if os.path.exists(final_path):
                print(f"⚠️  目标文件已存在: {final_filename}")
                # 生成备用文件名
                base_name, ext = os.path.splitext(final_filename)
                counter = 2
                while os.path.exists(final_path):
                    final_filename = f"{base_name}_{counter}{ext}"
                    final_path = os.path.join("media", final_filename)
                    counter += 1
                print(f"   使用备用文件名: {final_filename}")
            
            os.rename(temp_path, final_path)
            success_count += 1
            print(f"✅ {temp_filename.replace('TEMP_' + str(success_count-1) + '_', '')} → {final_filename}")
            
        except Exception as e:
            print(f"❌ 最终重命名失败 {temp_filename}: {e}")
            error_count += 1
    
    print(f"\n📊 修正完成:")
    print(f"   成功: {success_count} 个文件")
    print(f"   失败: {error_count} 个文件")
    
    if success_count > 0:
        verify_final_results()

def verify_final_results():
    """
    验证最终结果
    """
    files = get_current_files()
    print(f"\n🔍 验证结果:")
    print(f"   总文件数: {len(files)}")
    
    # 显示修正后的文件列表（前20个）
    print(f"   修正后的文件:")
    for i, file in enumerate(files[:20]):
        print(f"     {i+1:2d}. {file}")
    
    if len(files) > 20:
        print(f"     ... 还有 {len(files) - 20} 张图片")
    
    # 检查关键页码
    key_pages = ["P1-1", "P10-1", "P50-1", "P100-1", "P188-1"]
    print(f"\n   关键页码检查:")
    for page in key_pages:
        matching = [f for f in files if f.startswith(page)]
        if matching:
            print(f"     ✅ {page}: {matching[0]}")
        else:
            print(f"     ❌ {page}: 未找到")

def main():
    print(f"🚀 启动交互式图片页码修正工具")
    print(f"📝 这个工具将帮助您逐一确认每张图片的正确页码")
    print(f"💡 建议：在另一个窗口中打开Word文档，以便对照确认页码")
    
    ready = input(f"\n准备开始了吗？(Y/n): ").strip().lower()
    if ready == 'n':
        print(f"👋 下次再见！")
        return
    
    try:
        interactive_correction()
        print(f"\n🎉 交互式修正完成！")
        print(f"📁 所有修改已保存到 media 文件夹")
        print(f"💾 原始文件备份在 media_backup_interactive 文件夹")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")

if __name__ == "__main__":
    main()