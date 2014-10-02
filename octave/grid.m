function [vlines hlines]=grid(image,threshold,debug = 0)

%faz a soma em uma dimençao e detecta os picos 
graphv = sum(image,1);
graphv = moving_average(graphv,5);
peaksv = peakdet(graphv,threshold);
x = peaksv(:,1)';

graphh = sum(image,2);
graphh = moving_average(graphh,15);
peaksh = peakdet(graphh,threshold);
y = peaksh(:,1)';

if (debug)
  %desenha
  figure(1);
  imshow(~image);
  hold on;
  plot(1:size(image,2),graphv,"g");
  vline(x,'r');
  plot(graphh,1:size(image,1),"m");
  hline(y,'r');
  hold off;
endif

vlines=x;
hlines=y;