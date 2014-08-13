function res=extractFeatures(img)
b = mat2cell(img, repmat(16,[1 size(img,1)/16]), repmat(16,[1 size(img,2)/16]));
c = cellfun(@(m) sum(m(:)),b,'UniformOutput',false);
res = cell2mat(c)(:)';