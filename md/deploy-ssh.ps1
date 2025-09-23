# SSH deployment script
# Run this script to deploy via SSH

Write-Host "Connecting to server and deploying..." -ForegroundColor Blue

# Copy files to server
Write-Host "Copying deployment files to server..." -ForegroundColor Blue
scp -r backend\.env.production djangouser@167.235.140.125:~/peykan-tourism/backend/.env.production
scp docker-compose.production.yml djangouser@167.235.140.125:~/peykan-tourism/
scp deploy-server.sh djangouser@167.235.140.125:~/peykan-tourism/

# Execute deployment on server
Write-Host "Executing deployment on server..." -ForegroundColor Blue
ssh djangouser@167.235.140.125 "cd ~/peykan-tourism && chmod +x deploy-server.sh && ./deploy-server.sh"

Write-Host "SSH deployment completed!" -ForegroundColor Green
Write-Host "Check server status: ssh djangouser@167.235.140.125" -ForegroundColor Blue
Write-Host "View logs: ssh djangouser@167.235.140.125 'cd peykan-tourism && docker-compose -f docker-compose.production.yml logs -f'" -ForegroundColor Blue
