#AUTOGENERATED! DO NOT EDIT! File to edit: dev/11_vision_models_xresnet.ipynb (unless otherwise specified).

__all__ = ['init_cnn', 'XResNet', 'xresnet18', 'xresnet34', 'xresnet50', 'xresnet101', 'xresnet152']

#Cell
from ...torch_basics import *
from ...test import *

#Cell
def init_cnn(m):
    if getattr(m, 'bias', None) is not None: nn.init.constant_(m.bias, 0)
    if isinstance(m, (nn.Conv2d,nn.Linear)): nn.init.kaiming_normal_(m.weight)
    for l in m.children(): init_cnn(l)

#Cell
class XResNet(nn.Sequential):
    def __init__(self, expansion, layers, c_in=3, c_out=1000):
        stem = []
        sizes = [c_in,32,32,64]
        for i in range(3):
            stem.append(ConvLayer(sizes[i], sizes[i+1], stride=2 if i==0 else 1))

        block_szs = [64//expansion,64,128,256,512]
        blocks = [self._make_layer(expansion, block_szs[i], block_szs[i+1], l, 1 if i==0 else 2)
                  for i,l in enumerate(layers)]
        super().__init__(
            *stem,
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            *blocks,
            nn.AdaptiveAvgPool2d(1), Flatten(),
            nn.Linear(block_szs[-1]*expansion, c_out),
        )
        init_cnn(self)

    def _make_layer(self, expansion, ni, nf, blocks, stride):
        return nn.Sequential(
            *[ResBlock(expansion, ni if i==0 else nf, nf, stride if i==0 else 1)
              for i in range(blocks)])

#Cell
def _xresnet(pretrained, expansion, layers, **kwargs):
    assert not pretrained, 'Pretrained xresnet not yet available'
    return XResNet(expansion, layers, **kwargs)

def xresnet18 (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [2, 2,  2, 2], **kwargs)
def xresnet34 (pretrained=False, **kwargs): return _xresnet(pretrained, 1, [3, 4,  6, 3], **kwargs)
def xresnet50 (pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 4,  6, 3], **kwargs)
def xresnet101(pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 4, 23, 3], **kwargs)
def xresnet152(pretrained=False, **kwargs): return _xresnet(pretrained, 4, [3, 8, 36, 3], **kwargs)