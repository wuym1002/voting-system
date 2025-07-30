#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页码核对工具
帮助用户逐一核对图片的真实页码
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def get_sorted_files():
    """
    获取按当前页码排序的所有图片文件
    """
    media_dir = "media"
    if not os.path.exists(media_dir):
        print("❌ media文件夹不存在")
        return []
    
    files = []
    for file in os.listdir(media_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            files.append(file)
    
    # 按当前页码数字排序
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

def show_image_preview(filename):
    """
    显示图片预览
    """
    filepath = os.path.join("media", filename)
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    # 获取文件信息
    size = os.path.getsize(filepath)
    size_kb = size / 1024
    
    print(f"📷 图片信息:")
    print(f"   文件名: {filename}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   完整路径: {filepath}")
    
    # 尝试打开图片预览
    try:
        print(f"🔍 正在打开图片预览...")
        result = subprocess.run(['open', '-a', 'Preview', filepath], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ 图片已在Preview中打开")
            return True
        else:
            print(f"⚠️  Preview打开失败，尝试其他方式...")
    except Exception as e:
        print(f"⚠️  自动预览失败: {e}")
    
    # 备用方案：使用系统默认程序
    try:
        subprocess.run(['open', filepath], capture_output=True, timeout=3)
        print(f"✅ 图片已用默认程序打开")
        return True
    except:
        print(f"❌ 无法打开图片预览")
        return False

def verify_page_numbers():
    """
    核对页码的主要流程
    """
    files = get_sorted_files()
    if not files:
        print("❌ 没有找到图片文件")
        return
    
    print("🎯 页码核对工具")
    print("=" * 60)
    print(f"📊 找到 {len(files)} 张图片需要核对")
    print("💡 提示：请在另一个窗口打开Word文档，以便对照真实页码")
    print()
    
    # 创建备份
    backup_dir = "media_backup_verification"
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree("media", backup_dir)
    print(f"✅ 已创建备份到 {backup_dir}")
    
    corrections = []  # 存储需要修正的页码
    
    print("\n" + "=" * 60)
    print("开始逐一核对页码...")
    print("=" * 60)
    
    for i, filename in enumerate(files):
        try:
            # 提取当前页码
            current_page = 0
            if filename.startswith('P'):
                current_page_str = filename[1:].split('-')[0]
                current_page = int(current_page_str)
            
            print(f"\n📋 第 {i+1}/{len(files)} 张图片")
            print("─" * 40)
            print(f"当前文件名: {filename}")
            print(f"当前页码: P{current_page}")
            
            # 显示图片
            show_image_preview(filename)
            
            print(f"\n请选择操作:")
            print(f"1. 输入正确页码 (只输入数字，如: 25)")
            print(f"2. 当前页码正确 (按回车)")
            print(f"3. 跳过此图片 (输入 s)")
            print(f"4. 完成核对 (输入 q)")
            print(f"5. 显示当前进度 (输入 p)")
            
            while True:
                try:
                    user_input = input(f"\n请输入: ").strip()
                    
                    if user_input == "":
                        # 页码正确，不需要修改
                        print(f"✅ P{current_page} 页码正确")
                        break
                    elif user_input.lower() == 's':
                        print(f"⏭️  跳过 {filename}")
                        break
                    elif user_input.lower() == 'q':
                        print(f"🏁 用户选择完成核对")
                        return apply_corrections(corrections)
                    elif user_input.lower() == 'p':
                        print(f"📊 当前进度: {i+1}/{len(files)} ({(i+1)/len(files)*100:.1f}%)")
                        print(f"📝 已记录 {len(corrections)} 个修正")
                        continue
                    elif user_input.isdigit():
                        new_page = int(user_input)
                        if 1 <= new_page <= 1000:
                            corrections.append((filename, current_page, new_page))
                            print(f"📝 记录修正: {filename} → P{new_page}-1")
                            break
                        else:
                            print("❌ 页码应该在1-1000之间")
                    else:
                        print("❌ 无效输入，请重新选择")
                        
                except KeyboardInterrupt:
                    print(f"\n\n⏹️  用户中断核对")
                    if corrections:
                        save_choice = input("是否保存已核对的修正？(y/N): ").strip().lower()
                        if save_choice == 'y':
                            return apply_corrections(corrections)
                    return
                    
        except Exception as e:
            print(f"❌ 处理 {filename} 时出错: {e}")
            continue
    
    # 核对完成，应用修正
    return apply_corrections(corrections)

def apply_corrections(corrections):
    """
    应用页码修正
    """
    if not corrections:
        print(f"\n📋 没有需要修正的页码")
        return
    
    print(f"\n🔧 准备应用修正...")
    print(f"📋 需要修正 {len(corrections)} 张图片:")
    
    for filename, old_page, new_page in corrections:
        print(f"   {filename} → P{new_page}-1")
    
    confirm = input(f"\n确认应用这些修正吗？(y/N): ").strip().lower()
    if confirm != 'y':
        print(f"❌ 取消应用修正")
        return
    
    # 执行重命名
    success_count = 0
    temp_renames = []
    
    print(f"\n🔄 开始重命名...")
    
    # 第一步：重命名到临时文件名
    for filename, old_page, new_page in corrections:
        try:
            old_path = os.path.join("media", filename)
            if not os.path.exists(old_path):
                print(f"❌ 文件不存在: {filename}")
                continue
            
            # 获取扩展名
            _, ext = os.path.splitext(filename)
            
            # 临时文件名
            temp_filename = f"TEMP_{success_count}_{new_page}-1{ext}"
            temp_path = os.path.join("media", temp_filename)
            
            os.rename(old_path, temp_path)
            temp_renames.append((temp_filename, f"P{new_page}-1{ext}"))
            success_count += 1
            
        except Exception as e:
            print(f"❌ 重命名失败 {filename}: {e}")
    
    # 第二步：从临时文件名重命名到最终文件名
    final_success = 0
    for temp_filename, final_filename in temp_renames:
        try:
            temp_path = os.path.join("media", temp_filename)
            final_path = os.path.join("media", final_filename)
            
            # 处理文件名冲突
            counter = 1
            original_final = final_filename
            while os.path.exists(final_path):
                base_name, ext = os.path.splitext(original_final)
                final_filename = f"{base_name}_v{counter}{ext}"
                final_path = os.path.join("media", final_filename)
                counter += 1
            
            os.rename(temp_path, final_path)
            final_success += 1
            print(f"✅ {original_final}")
            
        except Exception as e:
            print(f"❌ 最终重命名失败: {e}")
    
    print(f"\n🎉 修正完成!")
    print(f"   成功修正: {final_success} 个文件")
    
    # 显示修正后的结果
    show_verification_results()

def show_verification_results():
    """
    显示核对结果
    """
    files = get_sorted_files()
    print(f"\n📊 核对后的结果:")
    print(f"   总文件数: {len(files)}")
    
    # 显示页码分布
    pages = []
    for file in files:
        if file.startswith('P'):
            try:
                page_num = int(file[1:].split('-')[0])
                pages.append(page_num)
            except:
                pass
    
    if pages:
        pages.sort()
        print(f"   页码范围: P{min(pages)} - P{max(pages)}")
        
        # 检查关键页码
        key_pages = [1, 10, 50, 100, 188, 200, 300]
        print(f"   关键页码检查:")
        for page in key_pages:
            if page in pages:
                print(f"     ✅ P{page}")
            else:
                print(f"     ❌ P{page} 缺失")

def main():
    print("🚀 页码核对工具")
    print("📝 这个工具将帮助您逐一核对每张图片的真实页码")
    print("💡 建议：打开Word文档以便对照确认")
    print()
    
    ready = input("准备开始核对吗？(Y/n): ").strip().lower()
    if ready == 'n':
        print("👋 下次见！")
        return
    
    try:
        verify_page_numbers()
        print(f"\n✨ 页码核对完成！")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 用户退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")

if __name__ == "__main__":
    main()