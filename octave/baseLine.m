function [y1 y2]=baseLine(image)

% Variaveis do GaGo

gaopt.InitialPopulation = [];
gaopt.EliteCount = 2;
gaopt.MutationFcn = 0.5;
gaopt.PopulationSize = 50;
gaopt.Generations =50;

tic
best = gaGo(@(arg)fitGrid(arg,image),22,gaopt);
toc

[y1 y2] = decode(best)

%desenha
figure(2);
imshow(~image);
hold on;
plot([1 size(image,2)],[y1 y2] ,"g");
hold off;
