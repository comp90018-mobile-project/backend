import os

os.system("docker stop comp90018-mobile-backend && docker rm comp90018-mobile-backend && docker image rm backend-comp90018-mobile-backend && docker-compose up -d")
os.system("docker logs -f comp90018-mobile-backend")