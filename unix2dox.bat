for /f "tokens=* delims=" %%a in ('dir "C:\Users\kelvinn\workspace\helomx" /s /b') do (
"C:\Program Files\unix2dos.exe" %%a
)

