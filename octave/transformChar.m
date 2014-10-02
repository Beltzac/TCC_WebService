function res=transformChar(img)
img(all(img==1,2),:)=[];
img(:,all(img==1,1))=[];
if (all(img == 0))
  res = ones(64);  
else
  img = mat2gray(img);
  res = imresize(img ,[64 64], 'nearest'); 
endif