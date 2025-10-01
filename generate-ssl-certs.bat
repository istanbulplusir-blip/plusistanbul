@echo off
REM Generate SSL certificates for development using Docker
REM This script creates self-signed certificates for local development

echo Generating SSL certificates for development...

REM Create SSL directory if it doesn't exist
if not exist nginx\ssl mkdir nginx\ssl

REM Use Docker to generate certificates
docker run --rm -v "%cd%\nginx\ssl:/ssl" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/key.pem -out /ssl/cert.pem -subj "/C=IR/ST=Tehran/L=Tehran/O=Peykan Tourism/OU=IT Department/CN=localhost"

echo SSL certificates generated successfully!
echo Certificate: nginx\ssl\cert.pem
echo Private Key: nginx\ssl\key.pem
echo.
echo Note: These are self-signed certificates for development only.
echo For production, use certificates from a trusted CA.

pause
