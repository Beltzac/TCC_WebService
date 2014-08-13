function [y1 y2]=decode(vector)

% quantos bits disponiveis a cada parametro
parameters =  vet2mat(vector,11);

y1 = bits2dec(parameters((1),:));
y2 = bits2dec(parameters((2),:));
