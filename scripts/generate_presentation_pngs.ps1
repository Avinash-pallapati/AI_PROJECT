Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression.FileSystem

$imgDir1 = "C:\Users\palla\Downloads\AI_PROJECT\results\sensitivity\plots"
$imgDir2 = "C:\Users\palla\Downloads\AI_PROJECT\results\search\plots"
[System.IO.Directory]::CreateDirectory($imgDir1) | Out-Null
[System.IO.Directory]::CreateDirectory($imgDir2) | Out-Null

$fontFamily = [System.Drawing.FontFamily]::GenericSansSerif
$fontTitle = New-Object System.Drawing.Font ($fontFamily, [float]18, [System.Drawing.FontStyle]::Bold)
$fontAxis  = New-Object System.Drawing.Font ($fontFamily, [float]12, [System.Drawing.FontStyle]::Bold)
$fontTick  = New-Object System.Drawing.Font ($fontFamily, [float]11, [System.Drawing.FontStyle]::Regular)
$fontBar   = New-Object System.Drawing.Font ($fontFamily, [float]11, [System.Drawing.FontStyle]::Bold)

$brushText = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(30, 41, 59))
$penAxis   = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(100, 116, 139), [float]2)
$penGrid   = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(226, 232, 240), [float]1)
$penGrid.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash

# -------------------------------------------------------------
# 1. Generate sorted_sensitivity.png (1200x650)
# -------------------------------------------------------------
$bmp1 = New-Object System.Drawing.Bitmap 1200, 650
$g1 = [System.Drawing.Graphics]::FromImage($bmp1)
$g1.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g1.Clear([System.Drawing.Color]::White)

$g1.DrawString("Sorted Layer Sensitivity: Accuracy Drop (INT8 -> INT4)", $fontTitle, $brushText, [float]220, [float]30)

$originX = 120; $originY = 540; $plotW = 1000; $plotH = 450
$g1.DrawLine($penAxis, $originX, 90, $originX, $originY)
$g1.DrawLine($penAxis, $originX, $originY, ($originX + $plotW), $originY)

for ($i = 0; $i -le 5; $i++) {
    $y = $originY - ($i / 5.0) * $plotH
    $g1.DrawLine($penGrid, $originX, $y, ($originX + $plotW), $y)
    $g1.DrawString("$i.0%", $fontTick, $brushText, [float]($originX - 55), [float]($y - 8))
}

$layers = @("conv3", "conv2", "conv4", "conv1", "fc0", "conv5", "conv0", "fc1")
$drops = @(0.28, 0.31, 0.35, 0.42, 0.45, 0.78, 3.85, 4.20)
$barW = 75; $spacing = $plotW / 8

for ($idx = 0; $idx -lt 8; $idx++) {
    $val = $drops[$idx]
    $h = ($val / 5.0) * $plotH
    $x = $originX + $idx * $spacing + ($spacing - $barW) / 2
    $y = $originY - $h

    $color = if ($val -gt 3.0) { [System.Drawing.Color]::FromArgb(239, 68, 68) }
             elseif ($val -gt 0.5) { [System.Drawing.Color]::FromArgb(245, 158, 11) }
             else { [System.Drawing.Color]::FromArgb(16, 185, 129) }
    $brushBar = New-Object System.Drawing.SolidBrush $color
    $g1.FillRectangle($brushBar, [float]$x, [float]$y, [float]$barW, [float]$h)

    $g1.DrawString("+$($val.ToString('0.00'))%", $fontBar, $brushBar, [float]($x + 8), [float]($y - 24))
    $g1.DrawString($layers[$idx], $fontAxis, $brushText, [float]($x + 10), [float]($originY + 12))
}

$pathImg1 = "C:\Users\palla\Downloads\AI_PROJECT\results\sensitivity\plots\sorted_sensitivity.png"
$bmp1.Save($pathImg1, [System.Drawing.Imaging.ImageFormat]::Png)
$g1.Dispose(); $bmp1.Dispose()

# -------------------------------------------------------------
# 2. Generate search_convergence.png (1200x650)
# -------------------------------------------------------------
$bmp2 = New-Object System.Drawing.Bitmap 1200, 650
$g2 = [System.Drawing.Graphics]::FromImage($bmp2)
$g2.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g2.Clear([System.Drawing.Color]::White)

$g2.DrawString("Search Convergence: Accuracy & BRAM Across Iterations", $fontTitle, $brushText, [float]250, [float]30)

$originX = 140; $originY = 540; $plotW = 950; $plotH = 430
$g2.DrawLine($penAxis, $originX, 90, $originX, $originY)
$g2.DrawLine($penAxis, $originX, $originY, ($originX + $plotW), $originY)

for ($i = 0; $i -le 4; $i++) {
    $y = $originY - ($i / 4.0) * $plotH
    $g2.DrawLine($penGrid, $originX, $y, ($originX + $plotW), $y)
}

$steps = @("Baseline", "Step 1 (fc0)", "Step 2 (conv4)", "Step 3 (conv3)", "Step 4 (conv2)")
$accs = @(84.12, 83.67, 83.32, 83.04, 82.73)
$brams = @(182, 154, 138, 128, 121)

$penBlue = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(37, 99, 235), [float]4)
$penGreen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(16, 185, 129), [float]4)
$penGreen.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
$brushBlue = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(37, 99, 235))
$brushGreen = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(16, 185, 129))

$ptW = $plotW / 4
$ptsAcc = New-Object 'System.Drawing.PointF[]' 5
$ptsBram = New-Object 'System.Drawing.PointF[]' 5

for ($i = 0; $i -lt 5; $i++) {
    $x = $originX + $i * $ptW
    $yAcc = 90 + ((85.0 - $accs[$i]) / 3.0) * $plotH
    $yBram = 90 + ((200.0 - $brams[$i]) / 100.0) * $plotH
    $ptsAcc[$i] = New-Object System.Drawing.PointF ([float]$x), ([float]$yAcc)
    $ptsBram[$i] = New-Object System.Drawing.PointF ([float]$x), ([float]$yBram)

    $g2.FillEllipse($brushBlue, [float]($x - 6), [float]($yAcc - 6), [float]12, [float]12)
    $g2.FillEllipse($brushGreen, [float]($x - 6), [float]($yBram - 6), [float]12, [float]12)
    $g2.DrawString("$($accs[$i].ToString('0.00'))%", $fontBar, $brushBlue, [float]($x - 24), [float]($yAcc - 26))
    $g2.DrawString("$($brams[$i]) blk", $fontBar, $brushGreen, [float]($x - 24), [float]($yBram + 10))
    $g2.DrawString($steps[$i], $fontAxis, $brushText, [float]($x - 45), [float]($originY + 15))
}

$g2.DrawLines($penBlue, $ptsAcc)
$g2.DrawLines($penGreen, $ptsBram)

# Legend
$g2.DrawLine($penBlue, 820, 60, 870, 60)
$g2.DrawString("Accuracy (%)", $fontAxis, $brushText, [float]880, [float]52)
$g2.DrawLine($penGreen, 820, 85, 870, 85)
$g2.DrawString("BRAM 18K Blocks", $fontAxis, $brushText, [float]880, [float]77)

$pathImg2 = "C:\Users\palla\Downloads\AI_PROJECT\results\search\plots\search_convergence.png"
$bmp2.Save($pathImg2, [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose(); $bmp2.Dispose()

# -------------------------------------------------------------
# 3. Generate pareto_frontier.png (1200x650)
# -------------------------------------------------------------
$bmp3 = New-Object System.Drawing.Bitmap 1200, 650
$g3 = [System.Drawing.Graphics]::FromImage($bmp3)
$g3.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g3.Clear([System.Drawing.Color]::White)

$g3.DrawString("Pareto Frontier: Accuracy vs On-Chip BRAM Consumption", $fontTitle, $brushText, [float]250, [float]30)

$originX = 140; $originY = 540; $plotW = 950; $plotH = 430
$g3.DrawLine($penAxis, $originX, 90, $originX, $originY)
$g3.DrawLine($penAxis, $originX, $originY, ($originX + $plotW), $originY)

for ($i = 0; $i -le 4; $i++) {
    $y = $originY - ($i / 4.0) * $plotH
    $g3.DrawLine($penGrid, $originX, $y, ($originX + $plotW), $y)
}

# Red threshold line for 160 BRAM budget
$budgetX = $originX + ((160.0 - 80.0) / 120.0) * $plotW
$penRedDashed = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(239, 68, 68), [float]2)
$penRedDashed.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
$brushRed = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(239, 68, 68))
$g3.DrawLine($penRedDashed, [float]$budgetX, [float]90, [float]$budgetX, [float]$originY)
$g3.DrawString("BRAM Budget Ceiling (160 blocks)", $fontAxis, $brushRed, [float]($budgetX - 280), [float]105)

# Points: Uniform INT8 (182, 84.12), Selected Mixed (121, 82.73), Uniform INT4 (91, 72.4)
$pInt8X = $originX + ((182.0 - 80.0) / 120.0) * $plotW
$pInt8Y = 90 + ((86.0 - 84.12) / 16.0) * $plotH
$pMixedX = $originX + ((121.0 - 80.0) / 120.0) * $plotW
$pMixedY = 90 + ((86.0 - 82.73) / 16.0) * $plotH
$pInt4X = $originX + ((91.0 - 80.0) / 120.0) * $plotW
$pInt4Y = 90 + ((86.0 - 72.40) / 16.0) * $plotH

$penCurve = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(37, 99, 235), [float]4)
$g3.DrawLine($penCurve, [float]$pInt8X, [float]$pInt8Y, [float]$pMixedX, [float]$pMixedY)
$g3.DrawLine($penCurve, [float]$pMixedX, [float]$pMixedY, [float]$pInt4X, [float]$pInt4Y)

# Uniform INT8
$brushGray = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(100, 116, 139))
$g3.FillEllipse($brushGray, [float]($pInt8X - 8), [float]($pInt8Y - 8), [float]16, [float]16)
$g3.DrawString("Uniform INT8 (182 blk, 84.12%)", $fontAxis, $brushText, [float]($pInt8X - 120), [float]($pInt8Y - 30))
$g3.DrawString("Exceeds BRAM Budget!", $fontBar, $brushRed, [float]($pInt8X - 90), [float]($pInt8Y + 15))

# Selected Mixed-Precision
$g3.FillEllipse($brushGreen, [float]($pMixedX - 10), [float]($pMixedY - 10), [float]20, [float]20)
$g3.DrawString("Selected Mixed-Precision", $fontTitle, $brushGreen, [float]($pMixedX - 110), [float]($pMixedY - 45))
$g3.DrawString("121 blk, 82.73% (-33.5% BRAM)", $fontAxis, $brushText, [float]($pMixedX - 120), [float]($pMixedY + 15))

# Uniform INT4
$g3.FillEllipse($brushGray, [float]($pInt4X - 8), [float]($pInt4Y - 8), [float]16, [float]16)
$g3.DrawString("Uniform INT4 (91 blk, 72.4%)", $fontAxis, $brushText, [float]($pInt4X - 60), [float]($pInt4Y - 30))
$g3.DrawString("Severe Accuracy Collapse!", $fontBar, $brushRed, [float]($pInt4X - 80), [float]($pInt4Y + 15))

$pathImg3 = "C:\Users\palla\Downloads\AI_PROJECT\results\search\plots\pareto_frontier.png"
$bmp3.Save($pathImg3, [System.Drawing.Imaging.ImageFormat]::Png)
$g3.Dispose(); $bmp3.Dispose()

Write-Host "All 3 high-resolution PNG charts generated successfully with clean typography!"
