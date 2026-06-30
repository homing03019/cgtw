$ErrorActionPreference = 'SilentlyContinue'

Add-Type @'
using System;
using System.Text;
using System.Diagnostics;
using System.Runtime.InteropServices;
public static class AutoYes {
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr hWndParent, EnumProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr hDlg, int nIDDlgItem);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern IntPtr PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
    public const uint BM_CLICK = 0x00F5;
    public const uint WM_COMMAND = 0x0111;
    public const int IDYES = 6;
    public static uint TargetPid = 0;
    public static IntPtr Dialog = IntPtr.Zero;

    public static bool HasYesText(IntPtr hWnd, IntPtr lParam) {
        var text = new StringBuilder(64);
        GetWindowText(hWnd, text, text.Capacity);
        var t = text.ToString();
        return t.Contains("\u662f") || t.Equals("Yes", StringComparison.OrdinalIgnoreCase) || t.Contains("&Yes");
    }

    public static bool HasDisclaimerText(IntPtr hWnd, IntPtr lParam) {
        var text = new StringBuilder(512);
        GetWindowText(hWnd, text, text.Capacity);
        var t = text.ToString();
        return t.Contains("\u5b66\u4e60") || t.Contains("\u5546\u4e1a") || t.Contains("\u672c\u7a0b\u5e8f")
            || t.Contains("\u4e25\u7981") || t.Contains("\u63d0\u793a");
    }

    public static bool FindDialog(IntPtr hWnd, IntPtr lParam) {
        if (!IsWindowVisible(hWnd)) return true;
        uint pid;
        GetWindowThreadProcessId(hWnd, out pid);
        if (TargetPid != 0 && pid != TargetPid) return true;

        var cls = new StringBuilder(64);
        GetClassName(hWnd, cls, cls.Capacity);
        if (cls.ToString() != "#32770") return true;

        bool disclaimer = false;
        bool yesButton = false;
        EnumChildWindows(hWnd, (child, p) => {
            if (HasDisclaimerText(child, p)) disclaimer = true;
            if (HasYesText(child, p)) yesButton = true;
            return true;
        }, IntPtr.Zero);

        var title = new StringBuilder(256);
        GetWindowText(hWnd, title, title.Capacity);
        if (!disclaimer && !title.ToString().Contains("\u63d0\u793a") && !yesButton) return true;

        Dialog = hWnd;
        return false;
    }

    public static bool TryDismiss() {
        Dialog = IntPtr.Zero;
        EnumWindows(FindDialog, IntPtr.Zero);
        if (Dialog == IntPtr.Zero) return false;

        SetForegroundWindow(Dialog);
        System.Threading.Thread.Sleep(80);

        var yes = GetDlgItem(Dialog, IDYES);
        if (yes != IntPtr.Zero) {
            SendMessage(yes, BM_CLICK, IntPtr.Zero, IntPtr.Zero);
            PostMessage(Dialog, WM_COMMAND, new IntPtr(IDYES), yes);
            return true;
        }

        EnumChildWindows(Dialog, (child, p) => {
            if (HasYesText(child, p)) {
                SendMessage(child, BM_CLICK, IntPtr.Zero, IntPtr.Zero);
                return false;
            }
            return true;
        }, IntPtr.Zero);
        return true;
    }
}
'@

$deadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $deadline) {
    $proc = Get-Process -Name 'cg2d' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc) {
        [AutoYes]::TargetPid = [uint32]$proc.Id
    }
    if ([AutoYes]::TryDismiss()) { break }
    Start-Sleep -Milliseconds 150
}
