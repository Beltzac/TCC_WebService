function [x popx fitvals] = gaGo(ffit, nbits, gaoptions, varargin)
%% Excencial of a Genetic Algorithm for Matlab or Gnu Octave %%%%%%%%%%%%%%%%%%%%%%
%% Laboratory of Bioinformatics UFPR/SEPT - Roberto Tadeu Raittz
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Runs a canonic (binary) genetic algorithm;
%
% Exemple:
%             x = gaGo(@fitnessfunc, numberofbits, gaoptions);
%
%  x receives numberofbits bits optimized according to the user function 'fitnessfunc';
%  gaoptions is an struct compatible with that generated by Matlab gaoptimset or 
%  one struct var that contains at least the parameters:
%
%       gaoptions.InitialPopulation
%       gaoptions.PopulationSize
%       gaoptions.Generations
%       gaoptions.EliteCount
%       gaoptions.MutationFcn
%          
%%%%%%
%
%Initialization
m = nbits;
n = gaoptions.PopulationSize;
nger = gaoptions.Generations;
mutrate = gaoptions.MutationFcn; %Uses only uniform mutation rate (number 0..1)
nelite = gaoptions.EliteCount;
% 
if isempty(gaoptions.InitialPopulation)
    pop0 = logical(randi(2,n,m)-1);
else
    pop0 = gaoptions.InitialPopulation;
end
if isempty(mutrate) || iscell(mutrate)
    mutrate = 0.15;
end    
if isempty(nelite)
    nelite = 2;
end    
nmut = fix(mutrate*n);
popx = pop0;
fits = zeros(n,1);
%
%Generations
for j=1:nger
    for i=1:n
        fits(i) = ffit(popx(i,:));
    end
    [xx iord] = sort(fits);
    %display([j xx(1)]);
    popx = popx(iord,:);
    newpop = popx;
    %  Crossover  
    i1 = randipow(n,1.3,n,1);
    i2 = randipow(n,1.3,n,1);
    pop1 = popx(i1,:);
    pop2 = popx(i2,:);
    icros = repmat(randi(m,n,1),1,m);
    ids = repmat(1:m,n,1);
    crt = (ids>icros);
    newpop(crt) = pop1(crt);
    newpop(~crt) = pop2(~crt);
    %  Mutation
    if nmut>0
        popmut = newpop(1:nmut,:);
        ids = find(popmut | ~popmut);
        xmut = randi(length(ids),nmut,1);
        popmut(xmut) = ~popmut(xmut);
    end
    %  Elitism
    if nelite>0
        newpop(1:nelite,:) = popx(1:nelite,:);
    end
    %  Make new population
    newpop(1+nelite:nelite+nmut,:) = popmut;
    popx = newpop;
end
% Returns
[fitvals iord] = sort(fits);
popx = popx(iord,:);
x = popx(1,:);

% Used for selection; see: http://www.sbgames.org/papers/sbgames08/posters/papers/p19.pdf
function mret = randipow(xmax,xpow,n, m)
mret = fix((xmax)*(rand(n,m).^xpow)) + 1;
