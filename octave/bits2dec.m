function mret = bits2dec(bits)
%Converte um vetor de bits para um inteiro

m = length(bits(1,:));
n = length(bits(:,1));
exp = repmat((2.^((1:m)-1)), n, 1);
mret = sum(exp.*bits,2);
