function [y1 y2]=baseLine(image)

% Variaveis do GaGo

gaopt.InitialPopulation = [];
gaopt.EliteCount = 2;
gaopt.MutationFcn = 0.5;
gaopt.PopulationSize = 100;
gaopt.Generations =100;

image = ~image;

tic
best = gaGo(@(arg)fitGrid(arg,image),22,gaopt);
toc

[y1 y2] = decode(best)

%desenha
figure(2);
imshow(~image);
hold on;
plot([1 size(image,2)],[y1 y2] ,"r");
hold off;
