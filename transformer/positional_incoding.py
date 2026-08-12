import numpy as np 


def positional_encoding(max_len, d_model):
        pos = np.arange(max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0)/d_model))
        pe = np.zeros((max_len, d_model))
        pe[:, 0::2] = np.sin(pos + div_term)
        pe[:, 1::2] = np.cos(pos + div_term)
        
        return pe







# example usage

max_len = 50 #sequence length
d_model = 512 # embadding dimention
pe = positional_encoding(max_len, d_model)
print(pe.shape) # OUtput: (50, 512)


