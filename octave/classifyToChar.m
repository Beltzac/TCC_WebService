function res=classifyToChar(att,cc)
guess = test_sc(cc, att);
guess = guess.classlabel;
if (guess == 1)
res = " ";
elseif (guess == 2)
res = "A";
elseif (guess == 3)
res = "C";
elseif (guess == 4)
res = "G";
elseif (guess == 5)
res = "T";
endif