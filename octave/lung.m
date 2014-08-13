function [vlines hlines]=lung(image,threshold)

%faz a soma em uma dimençao e detecta os picos 
graphv = sum(image,1);
graphv = moving_average(graphv,5);
peaksv = peakdet(graphv,threshold);

graphh = sum(image,2);
graphh = moving_average(graphh,15);
peaksh = peakdet(graphh,threshold);

%desenha
figure(1);
imshow(~image);
hold on;
plot(1:size(image,2),graphv,"g");
x = peaksv(:,1)';
vline(x,'r');

plot(graphh,1:size(image,1),"m");
y = peaksh(:,1)';
hline(y,'r');
hold off;

vlines=x;
hlines=y;