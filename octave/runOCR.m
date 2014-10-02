function [texto, tempo]  = runOCR(image_path,debug = 0)
tic

pkg load all;
format compact;

%carrega imagem
img = imread(image_path);

img = rgb2gray(img);
sizeImg = size(img);

%preto e branco(rgb pra binario)
imgBitOri = img;

imgBitOri = im2bw((imgBitOri),graythresh (imgBitOri));

imgBitOri = bwmorph(imgBitOri,'close');
imgBitOri = bwmorph(imgBitOri,'erode',12);

[imgBitOri thresh] = edge(mat2gray(imgBitOri),"canny");

#imgBitOri = bwmorph(imgBitOri,'dilate');

#H = houghtf (imgBitOri);
H = houghtf(imgBitOri);
I = houghpeaks(H, 5);
rh = I(:,1);
th = I(:,2);

angle = normalizeAngle( mean(th) ) * 180/pi + 90;

if (debug)

  %desenha
  figure(2);
  imshow(imgBitOri);
  
  hold on; 
  
 
  hold off;

  %desenha
  figure(6);
  hold on;
  colormap('hot');
  imagesc(H);
  scatter(th ,rh ,'g');
  hold off;
endif



%remove ruido
#imgBitOri = medfilt2(imgBitOri, [7 7]);
#imgBitOri = bwmorph(imgBitOri,'close');
#imgBitOri = bwmorph(imgBitOri,'erode',10);


#[y1 y2] = baseLine(imgBitOri);
#angle = 180 + lineAngle(1,y1,sizeImg(2),y2)


img = imrotate(img,angle,"cubic","crop");
sizeImg = size(img);

%preto e branco(rgb pra binario)
imgBitOri = im2bw((img),graythresh (img));

%remove ruido
#imgBitOri = medfilt2(imgBitOri, [3 3]);
imgBitOri = bwmorph(imgBitOri,'close');

[vlines hlines] = grid(imgBitOri,100,debug);

vlines = [1 vlines sizeImg(2)+1];
hlines = [1 hlines sizeImg(1)+1];

diffv = diff(vlines);
diffh = diff(hlines);

letras = mat2cell(imgBitOri,diffh,diffv);

%remove linhas e colunas que ficaram muito diferente da media
mv = mean(diffv);
removev = find(diffv > mv + mv *0.20 | diffv < mv - mv * 0.40);
mh = mean(diffh);
removeh = find(diffh > mh + mh *0.20 | diffh < mh - mh * 0.40);
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
if (debug)
  figure(5);
  imshow(~cell2mat(transformedChars));
endif

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
size_features = size(features);
features = cell2mat(features(:));
guess = test_sc(cc, features);
guess = guess.classlabel;
chars2 = arrayfun(@(m) classifyToChar(m),guess,'UniformOutput',false);
reshape(cell2mat(chars2),size_features);
tempo = toc
texto = reshape(cell2mat(chars2),size_features);



