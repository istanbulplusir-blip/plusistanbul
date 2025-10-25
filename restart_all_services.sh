#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Restart تمام سرویس‌ها${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# مرحله 1: نمایش وضعیت فعلی
echo -e "${BLUE}📋 مرحله 1: وضعیت فعلی سرویس‌ها${NC}"
docker-compose -f docker-compose.production-secure.yml ps
echo ""

# مرحله 2: Restart Backend
echo -e "${BLUE}🔄 مرحله 2: Restart Backend...${NC}"
docker-compose -f docker-compose.production-secure.yml restart backend
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend restart شد${NC}"
else
    echo -e "${RED}❌ خطا در restart کردن Backend${NC}"
fi
echo ""

# صبر کردن برای آماده شدن backend
echo -e "${YELLOW}⏳ صبر برای آماده شدن Backend...${NC}"
sleep 5

# مرحله 3: Restart Frontend
echo -e "${BLUE}🔄 مرحله 3: Restart Frontend...${NC}"
docker-compose -f docker-compose.production-secure.yml restart frontend
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend restart شد${NC}"
else
    echo -e "${RED}❌ خطا در restart کردن Frontend${NC}"
fi
echo ""

# صبر کردن برای آماده شدن frontend
echo -e "${YELLOW}⏳ صبر برای آماده شدن Frontend...${NC}"
sleep 5

# مرحله 4: Restart Nginx
echo -e "${BLUE}🔄 مرحله 4: Restart Nginx...${NC}"
docker-compose -f docker-compose.production-secure.yml restart nginx
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx restart شد${NC}"
else
    echo -e "${RED}❌ خطا در restart کردن Nginx${NC}"
fi
echo ""

# مرحله 5: Restart Redis (اختیاری)
echo -e "${BLUE}🔄 مرحله 5: Restart Redis...${NC}"
docker-compose -f docker-compose.production-secure.yml restart redis
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Redis restart شد${NC}"
else
    echo -e "${YELLOW}⚠️  هشدار: مشکل در restart کردن Redis${NC}"
fi
echo ""

# مرحله 6: بررسی وضعیت نهایی
echo -e "${BLUE}📊 مرحله 6: بررسی وضعیت نهایی${NC}"
sleep 3
docker-compose -f docker-compose.production-secure.yml ps
echo ""

# مرحله 7: تست سلامت سرویس‌ها
echo -e "${BLUE}🏥 مرحله 7: تست سلامت سرویس‌ها${NC}"
echo ""

# تست Backend
echo -e "${YELLOW}تست Backend...${NC}"
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/api/v1/health/)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Backend سالم است (HTTP $BACKEND_STATUS)${NC}"
else
    echo -e "${RED}❌ Backend مشکل دارد (HTTP $BACKEND_STATUS)${NC}"
fi

# تست Frontend (از طریق Nginx)
echo -e "${YELLOW}تست Frontend...${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Frontend سالم است (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}❌ Frontend مشکل دارد (HTTP $FRONTEND_STATUS)${NC}"
fi

# تست API
echo -e "${YELLOW}تست API...${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://peykantravelistanbul.com/api/v1/tours/)
if [ "$API_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ API سالم است (HTTP $API_STATUS)${NC}"
else
    echo -e "${RED}❌ API مشکل دارد (HTTP $API_STATUS)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Restart تکمیل شد!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📝 لینک‌های مفید:${NC}"
echo -e "   • سایت: ${YELLOW}https://peykantravelistanbul.com${NC}"
echo -e "   • Admin: ${YELLOW}https://peykantravelistanbul.com/admin/${NC}"
echo -e "   • API: ${YELLOW}https://peykantravelistanbul.com/api/v1/tours/${NC}"
echo ""
echo -e "${BLUE}📊 دستورات مفید:${NC}"
echo -e "   • مشاهده لاگ Backend: ${YELLOW}docker-compose -f docker-compose.production-secure.yml logs -f backend${NC}"
echo -e "   • مشاهده لاگ Frontend: ${YELLOW}docker-compose -f docker-compose.production-secure.yml logs -f frontend${NC}"
echo -e "   • مشاهده لاگ Nginx: ${YELLOW}docker-compose -f docker-compose.production-secure.yml logs -f nginx${NC}"
echo -e "   • بررسی وضعیت: ${YELLOW}docker-compose -f docker-compose.production-secure.yml ps${NC}"
echo ""
echo -e "${GREEN}موفق باشید! 🎉${NC}"
