# Resources

- **LITERATURE**
  - **LLM-based HDL Generation**
    - Pearce H., et.al. _AutoChip: Automating HDL Generation Using LLM Feedback_ in DAC ’24([Link-To-Rxiv](https://arxiv.org/pdf/2311.04887))
    - Pearce H., et.al., “_DAVE: Deriving Automatically Verilog from English_,” MLCAD ’20. ([Link](https://dl.acm.org/doi/10.1145/3380446.3430634))
    - S. Thakur et al., “_Benchmarking Large Language Models for Automated Verilog RTL Code Generation_,” DATE'23 ([PDF](https://arxiv.org/pdf/2212.11140))

  - **Keyword Spotting**
    -  Chong, Y. S., et.al. "_0.08mm² 128nW MFCC engine for ultra‑low power, always‑on smart sensing applications_". ISCAS-2022 ([PDF](https://dr.ntu.edu.sg/bitstream/10356/159307/2/MFCC%20Engine%20for%20Ultra-low%20Power%2C%20Always-on%20Smart%20Sensing%20Applications%20%28final%20checked%29.pdf))
    -  G. Sharma, wt.al., “_Trends in audio signal feature extraction methods_,” Applied Acoustics, vol. 158, p. 107020, Jan. 2020. ([PDF](https://calebrascon.info/AR/Topic4/addresources/features.pdf), [Link](https://doi.org/10.1016/j.apacoust.2019.107020)) : Nice summary article with a great summary of algorithms for feature extraction.
    - Y. Zhang, et.al., “_Hello Edge: Keyword Spotting on Microcontrollers_,” Feb. 14, 2018, arXiv ([PDF](https://arxiv.org/pdf/1711.07128) | [Link](https://arxiv.org/abs/1711.07128) | [Code GitHub Page](https://github.com/ARM-software/ML-KWS-for-MCU) | [PaperSwitchCode](https://paperswithcode.com/paper/hello-edge-keyword-spotting-on)) : KWS immplementation on resource-contrained microconrollers.
    - W. Han, et.al., “_An efficient MFCC extraction method in speech recognition_,” ISCAS, 2006, ([Link](https://doi.org/10.1109/ISCAS.2006.1692543) | [PDF](https://www.academia.edu/download/31107261/1660.pdf)) : An efficient algorithm to calculate the Mel-Frequency Cepstrum Coeffs (MFCC). 

- **DATASHEETS/APP NOTES**
  - Datasheet: **TDK InvenSense ICS-43434** : I2S Digital Output MEMS Microphone.  ([Digikey Link](https://www.digikey.in/en/products/detail/tdk-invensense/ICS-43434/6140298), [PDF](https://invensense.tdk.com/wp-content/uploads/2016/02/DS-000069-ICS-43434-v1.2.pdf?ref_disty=digikey))
  - Datasheet: **Knowles SPH0645LM4H-B** : I2S Digital Output MEMS Microphone. ([Digikey Link](https://www.digikey.in/en/products/detail/knowles/SPH0645LM4H-B/5332440), [PDF](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/908/SPH0645LM4H-B.pdf))
 

- **USEFUL LINKS**
  - [Priyansu's KWS Github Page](https://github.com/Priyansu122/Project_keywordSpotter)
  - [Priyansu's RTL2GDS Github Page](https://github.com/Priyansu122/SI2024_RTL_TO_GDS)
  - [Priyansu's RTL2FPGA Github Page](https://github.com/Priyansu122/ASIC_FPGA_Design_Flow)

 
# Keyword Spotting (KWS) Architecture

![KWS Archh](doc/KWS-architecture.svg)

Mel frequency cepstral coefficient (MFCC) features are widely used in applications such as keyword spotting (KWS) for extracting speech features such as a simple word "Alexa". In a typical all-digital immplementation, a digital microphone is used to read real-time data using an $I^2S$ serial interface. The serial data is converted to parallel bytes. 

The first operation done on the input data is a pre-emphasis filter (high-pass or HPF) to remove the DC content from the signal. The pre-emphasis filter is typicall implemented as the following difference equation: 

$y(n) = x(n) - \alpha x(n-1)$

where $\alpha$ ranges from 0.9-1. To keep the hardware minimal, the fraction is implemented as a shift+add. For eg. $y(n) = x(n) - ( x(n) - x(n)/32 )$ which is a shift and add operation to realize $\alpha = 31/32 = 0.96875$

After the pre-emphasis filter, the data is multiplied with a _window (hamming, hanning, etc.))_ to avoid spectral leakage from FFT operation. After the windowing, fast-fourier transform (FFT) is applied to the signal to find the frequency content of the signal. Then the linear frequency scale if converted to _Mel Log scale_ ( $Mel(f) = 2595 \cdot log_{10}(1 + f/700)$ ) to mimic the human ear perception. Then the _log_ of Mel frequency power is calculated and the DCT operation is done to generate the MFCC co-efficients. Finally, the MFCC co-efficients are used to classify the voice signal using a classifier such as Convolution Neural Netwrk (CNN), etc.

Typically the MFCC and the classifier are implemented on the _Edge Node_ using a microcontroller. But with more and more computing moving to the edge, we are now at a point where some of the trivial or not-so-trivial computing to move to the sensor itself. In this work we propose to move some of the front-end signal processing (HPF, wondowing and FFT) to the microphone itself which may call as _Bleeding-Edge Computing_. 

# Proposed "Bleeding-Edge Computing" Architecture

The goal of this work is to create a minimalistic hardware for a microphone to read the FFT bins directly which can be used in the subsequent stages of the KWS architecutre on the host processor. This minimalist harware may come at an expense of accuracy but that is a trade-off often acceptable at system level, if available. Also, a longer term goal is to integrate the entire KWS architecture in the microphone that can run off energy harvested off the microphone itself, for example in piezo-electric microphones. 

This architecture was simulated using Python to optimize the hardware without losing significant accuracy. As the parameters were varied, the output spectogram (FFT vs. time) was visually inspected to make sure the harward-reduction-to-accuracy ratio was maximized. The following parameters were minimized which directly impacts the hardware:

- **Input sampling frequency**: Typical audio sampling is 44.4kHz but it was found that even **4 kHz** does not result in siginificant loss in FFT accuracy. This will result in almost a 10X reduction of HW.
- **Input data width**: Typical microphone data-width is 24-bit but linear only up to 10-11 bit but, **7-bit** data-width seems a good compromise.
- **FFT data-point**: Typically 128-point or 256-point FFT are used but even going down to **32-point** seems still a good choice.

## Block Specs

- **I2S to 7-bit** data de-serializer : There are 3 signals provided to the microphone, **WS, SCK, SD**. In mono mode, the WS signal is pulled low for 32 cycles and pulled high for 32 cycles. During the WS low period, 7-b MSB data is latched internally. The WS period is the sampling frequency ie. **4 kHz**.
- **Pre-emphasis filter (HPF)**: Realize the following difference equation: $y(n) = x(n) - ( x(n) - x(n)/32 )$
- **Hanning Window**: The serial data is fed to **32-byte pipeline** that is multiplied with the 32-byte pipeline register.
- **32-point FFT $R2^2SDF$** : $R2^2SDF$ FFT is an architecture that realizes the FFT algorithm with minimal hardware.
