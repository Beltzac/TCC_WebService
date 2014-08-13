function mret = fitGrid(arg,image)

[y1 y2] = decode(arg);

sizeImg = size(image);

lineResolution = 500;

%calcula as coordenadas por onde a linha passa
x = linspace(1,sizeImg(1),lineResolution);
y = linspace(y1,y2,lineResolution);

%concatena
xy = [x' y'];

%remove pontos que ficaram fora da imagem central
[rows, cols] = find(xy(:,1) > sizeImg(2) | xy(:,2) > sizeImg(1) | xy(:,1) < 1 | xy(:,2) < 1);
xy(rows,:) = [] ;

%transforma os pontos em im index linear
idx = sub2ind(sizeImg,round(xy(:,2)),round(xy(:,1)));

%procura o que tem embaixo das linhas
line_points = numel(idx);
white = sum(image(idx));
black = line_points - white;

%calcula nota

mret = -black;
