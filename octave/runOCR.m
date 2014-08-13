function [texto, tempo]  = runOCR(image_path)
tic

pkg load all;
format compact;

%carrega imagem
img = imread(image_path);

img = rgb2gray(img);

%preto e branco(rgb pra binario)
imgBitOri = im2bw((img),graythresh (img));

%remove ruido
imgBitOri = medfilt2(imgBitOri, [7 7]);


sizeImg = size(img);
[y1 y2] = baseLine(imgBitOri);
angle = 180 + lineAngle(1,y1,sizeImg(2),y2);

%remove as duas linhas mais diferentes e faz a media
angle = mean(angle)

img = imrotate(img,angle);
sizeImg = size(img);

%preto e branco(rgb pra binario)
imgBitOri = im2bw((img),graythresh (img));

%remove ruido
imgBitOri = medfilt2(imgBitOri, [3 3]);

[vlines hlines] = lung(imgBitOri,60);

vlines = [1 vlines sizeImg(2)+1];
hlines = [1 hlines sizeImg(1)+1];

diffv = diff(vlines);
diffh = diff(hlines);

letras = mat2cell(imgBitOri,diffh,diffv);

%remove linhas e colunas que ficaram muito diferente da media
mv = mean(diffv);
removev = find(diffv > mv + mv *0.20 | diffv < mv - mv * 0.20)
mh = mean(diffh);
removeh = find(diffh > mh + mh *0.20 | diffh < mh - mh * 0.20)
letras(removeh,:) = 0;
letras(:,removev) = 0;

#{
figure(3);
imshow(~cell2mat(letras(2,3)));
#}

transformedChars = cellfun(@(m) transformChar(m),letras,'UniformOutput',false);

#{
figure(4);
imshow(~transformedChars{2,3});
#}

figure(5);
imshow(~cell2mat(transformedChars));

features = cellfun(@(m) extractFeatures(m),transformedChars,'UniformOutput',false);

#{

class = [];
for i = 1:size(transformedChars,1)
  for j = 1:size(transformedChars,2)
   figure(6);
   imshow(~transformedChars{i,j});
    if(all(transformedChars{i,j} == 0) | all(transformedChars{i,j} == 1))  
   r = 1;
  else 
   r = menu ("Class?", "Empty", "A","C","G","T");
   endif
   class(end+1,:) = [features{i,j} r];
  endfor
endfor

w2weka(class,"class");
#}

load cc.dat;
chars = cellfun(@(m) classifyToChar(m,cc),features,'UniformOutput',false);

tempo = toc
texto = cell2mat(chars);


