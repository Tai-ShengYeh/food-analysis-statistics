$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$downloadDir = Join-Path $projectRoot "downloads"
New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

$chapters = Get-ChildItem -LiteralPath (Join-Path $projectRoot "R") -Filter "ch*.R" -File |
  Sort-Object Name
$extensions = Get-ChildItem -LiteralPath (Join-Path $projectRoot "R") -Filter "extension_*.R" -File |
  Sort-Object Name
$programs = @($chapters) + @($extensions)

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("# 食品分析數據品管與量測不準度：R 程式全集")
$lines.Add("")
$lines.Add("> 適用對象：沒有程式基礎的大學生。必修課程與實務案例使用 R 內建函數；選修 metRology 工具箱需要額外套件。")
$lines.Add("")
$lines.Add("## 使用方式")
$lines.Add("")
$lines.Add("1. 安裝 R，開啟 RGui 或 RStudio。")
$lines.Add("2. 從第一章開始，一次複製一小段到 Console 後按 Enter。")
$lines.Add("3. 先預測輸出，再執行；圖形會出現在 Plots 或新的繪圖視窗。")
$lines.Add("4. 若中文圖形在舊版 Windows 顯示亂碼，請以 UTF-8 儲存並在 RStudio 執行。")
$lines.Add("")
$lines.Add("## 教材來源與界線")
$lines.Add("")
$lines.Add("- Nielsen's Food Analysis, Chapter 4, Evaluation of Analytical Data：第 1–5 章。")
$lines.Add("- Eurachem/CITAC Guide CG4, Quantifying Uncertainty in Analytical Measurement, Third Edition (2012)：第 6–10 章。")
$lines.Add("- CRAN metRology 0.9-29-2 官方文件：選修延伸單元；版本更新時請重新核對函數說明。")
$lines.Add("- 天平、酸鹼滴定與 HPLC 案例依 QUAM 建模、量化、合成與報告原則自編；正式作業須換成實驗室資料。")
$lines.Add("- 程式為教學性改寫；LOD、異常值、涵蓋因子與符合性判定須依實驗室程序與適用法規確認。")
$lines.Add("")

foreach ($chapter in $programs) {
  $title = (Get-Content -LiteralPath $chapter.FullName -Encoding UTF8 | Select-Object -First 3 | Select-Object -Last 1) -replace '^#\s*', ''
  $lines.Add("---")
  $lines.Add("")
  $lines.Add("## $($chapter.BaseName)：$title")
  $lines.Add("")
  $lines.Add('```r')
  foreach ($line in Get-Content -LiteralPath $chapter.FullName -Encoding UTF8) { $lines.Add($line) }
  $lines.Add('```')
  $lines.Add("")
}

$lines.Add("## 建議的期末提交格式")
$lines.Add("")
$lines.Add("請提交：原始數據、可重現 R 程式、必要圖形、結果與單位、不準度及涵蓋資訊、品管判讀、決策規則，以及限制說明。")
$lines | Set-Content -LiteralPath (Join-Path $downloadDir "food-analysis-statistics-R.md") -Encoding UTF8
