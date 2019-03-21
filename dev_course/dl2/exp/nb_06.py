
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/06_cuda_cnn_hooks_init.ipynb

from exp.nb_05 import *
torch.set_num_threads(2)

def normalize_to(train, valid):
    m,s = train.mean(),train.std()
    return normalize(train, m, s), normalize(valid, m, s)

class Lambda(nn.Module):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def forward(self, x): return self.func(x)

def flatten(x):      return x.view(x.shape[0], -1)

class CudaCallback(Callback):
    def begin_fit(self, run): run.model.cuda()
    def begin_batch(self, run): run.xb,run.yb = run.xb.cuda(),run.yb.cuda()

class BatchTransformXCallback(Callback):
    _order=2
    def __init__(self, tfm): self.tfm = tfm
    def begin_batch(self, run): run.xb = self.tfm(run.xb)

def resize_tfm(*size):
    def _inner(x): return x.view(*((-1,)+size))
    return _inner

def children(m): return list(m.children())

class Hook():
    def __init__(self, m, f):
        self.means = []
        self.stds  = []
        self.hook = m.register_forward_hook(partial(f, self))

    def remove(self): self.hook.remove()
    def __del__(self): self.remove()

from torch.nn import init

class Hooks():
    def __init__(self, ms, f): self.hooks = [Hook(m, f) for m in ms]
    def __getitem__(self,i): return self.hooks[i]
    def __len__(self): return len(self.hooks)
    def __iter__(self): return iter(self.hooks)
    def __enter__(self, *args): return self
    def __exit__ (self, *args): self.remove()

    def remove(self):
        for h in self.hooks: h.remove()

def get_cnn_layers(data, nfs, **kwargs):
    nfs = [1] + nfs
    return [conv2d(nfs[i], nfs[i+1], **kwargs)
            for i in range(len(nfs)-1)] + [
        nn.AdaptiveAvgPool2d(1), Lambda(flatten), nn.Linear(nfs[-1], data.c)]

def get_cnn_model(data, nfs, **kwargs): return nn.Sequential(*get_cnn_layers(data, nfs, **kwargs))

def conv2d(ni, nf, ks=3, stride=2, **kwargs):
    return nn.Sequential(
        nn.Conv2d(ni, nf, ks, padding=ks//2, stride=stride), GeneralRelu(**kwargs))

class GeneralRelu(nn.Module):
    def __init__(self, leak=None, sub=None, maxv=None):
        super().__init__()
        self.leak,self.sub,self.maxv = leak,sub,maxv

    def forward(self, x):
        x = F.leaky_relu(x,self.leak) if self.leak is not None else F.relu(x)
        if self.sub is not None: x.sub_(self.sub)
        if self.maxv is not None: x.clamp_max_(self.maxv)
        return x