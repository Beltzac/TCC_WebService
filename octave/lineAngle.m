function res=lineAngle(x1,y1,x2,y2)
xDiff = x1 - x2; 
yDiff = y1 - y2;  
res = (atan2(yDiff, xDiff))/pi*180;