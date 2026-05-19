# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import winreg

def find_edge_exe():
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe")
        value, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if value and os.path.exists(value):
            return value
    except:
        pass
    return None

def create_edge_shortcut():
    edge_path = find_edge_exe()
    if not edge_path:
        print("[ERROR] Cannot find Microsoft Edge installation")
        return False
    desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
    shortcut_name = "Edge (解锁Cookie) - 视频下载器专用.lnk"
    shortcut_path = os.path.join(desktop, shortcut_name)
    target = f'"{edge_path}" --disable-features=LockProfileCookieDatabase'
    try:
        import pythoncom
        from win32com.client import Dispatch
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = edge_path
        shortcut.Arguments = '--disable-features=LockProfileCookieDatabase'
        shortcut.Description = 'Edge (Cookie已解锁) - 用于视频下载器自动读取登录状态'
        shortcut.IconLocation = f'{edge_path},0'
        shortcut.Save()
        print(f"[SUCCESS] Created shortcut: {shortcut_path}")
        return True
    except ImportError:
        try:
            vbs_content = f'''Set shell = CreateObject("WScript.Shell")
Set shortcut = shell.CreateShortcut("{shortcut_path}")
shortcut.TargetPath = "{edge_path}"
shortcut.Arguments = "--disable-features=LockProfileCookieDatabase"
shortcut.Description = "Edge (Cookie已解锁) - 用于视频下载器自动读取登录状态"
shortcut.IconLocation = "{edge_path},0"
shortcut.Save()
MsgBox "快捷方式已创建到桌面！\\n\\n请使用这个新快捷方式启动 Edge，\\n视频下载器就可以在 Edge 运行时读取 Cookie 了。", vbInformation, "配置成功"'''
            vbs_path = os.path.join(os.environ.get('TEMP', ''), 'create_edge_shortcut.vbs')
            with open(vbs_path, 'w', encoding='utf-8') as f:
                f.write(vbs_content)
            subprocess.run(['cscript', '//nologo', vbs_path], check=True)
            os.remove(vbs_path)
            print(f"[SUCCESS] Created shortcut via VBS: {shortcut_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create shortcut: {e}")
            return False

def main():
    print("=" * 50)
    print("  Edge 浏览器 Cookie 解锁工具")
    print("  让视频下载器可以在 Edge 运行时读取 Cookie")
    print("=" * 50)
    print()
    edge_path = find_edge_exe()
    if edge_path:
        print(f"[INFO] Found Edge: {edge_path}")
    else:
        print("[ERROR] 未找到 Edge，请确认已安装 Microsoft Edge")
        input("\n按回车键退出...")
        return
    print()
    print("[*] 正在创建桌面快捷方式...")
    print()
    if create_edge_shortcut():
        print()
        print("=" * 50)
        print("  配置完成！")
        print("=" * 50)
        print()
        print("  使用方法：")
        print("  1. 关闭当前正在运行的 Edge 浏览器")
        print("  2. 双击桌面上的 [Edge (解锁Cookie)] 快捷方式启动 Edge")
        print("  3. 在设置页选择浏览器为 [Microsoft Edge]")
        print("  4. 现在可以正常下载需要登录的视频了！")
        print()
        print("  注意：使用普通方式启动的 Edge 仍然会锁定 Cookie")
        print("       只有通过这个快捷方式启动的 Edge 才会解锁")
        print()
    else:
        print()
        print("[FAILED] 创建失败，请尝试：")
        print("  1. 右键点击此脚本 -> 以管理员身份运行")
        print("  2. 或手动创建 Edge 快捷方式并添加参数:")
        print('     --disable-features=LockProfileCookieDatabase')
        print()
    input("按回车键退出...")

if __name__ == '__main__':
    main()
