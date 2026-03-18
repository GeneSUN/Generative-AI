
## 1. Adapts language models, T5
## 2. Tokenize input time series: 

Mapping the observations xi ∈R to a finite set of tokens, convert regression to classification

```
[100, 110, 120, 130]

1. Scaling

s = mean(|x|) = (100 + 110 + 120 + 130) / 4 = 115
[100/115, 110/115, 120/115, 130/115] ≈ [0.87, 0.96, 1.04, 1.13]

2. Quantization

Bin 1 → [-15, -12]
Bin 2 → [-12, -9]
...
Bin 6 → [0, 1]
...
Bin 10 → [12, 15]

Result:
[6, 6, 7, 7]
```

For quantization, The design of bin can either be Quantile-dependent or uniform.
Since the distribution of values for unseen downstream datasets can differ significantly from the training distribution, we opt for uniform binning in our experiments,

## 3. Objective Function

$$\ell(\theta) = - \sum_{h=1}^{H+1} \sum_{i=1}^{|V_{ts}|} \mathbf{1}_{(z_{C+h+1}=i)} \log p_{\theta}(z_{C+h+1}=i \mid z_{1:C+h})$$

- This is classification loss function, instead of regression
- This categorical cross entropy loss is not a **distance-aware objective function.**
- The ordinal is expect on distribution of bin indices, adjacent bin is expected to have higher conditional probability
```
P(bin 3 | bin 2) = 0.5  
P(bin 4 | bin 2) = 0.3  
P(bin 5 | bin 2) = 0.2 
```

## 4. Forecasting

###  Autoregressive sampling generates one future trajectory

1. [2, 3, 3] -> sample P(next token |[2, 3, 3] ) -> 4
2. [2, 3, 3, 4] -> sample P(next token |[2, 3, 3, 4] ) -> 4
3. [2, 3, 3, 4, 4] -> sample P(next token |[2, 3, 3, 4, 4] ) -> 5
4. final series [2, 3, 3, **4, 4, 5**]


### Repeating sampling produces multiple realizations (possible futures)

Run 1 → [2, 3, 3, 4,5,4]
Run 2 → [2, 3, 3, 3,4,4]
Run 3 → [2, 3, 3, 4,4,5]
...


### Aggregating these realizations approximates the predictive distribution


## Data Augmentation
1. Synthesis Data
2. Augmented Data
3. Diverse Real Data

## Summary

Chronos is a good choice when:

1. You want a strong **zero-shot/cold start** baseline fast, without building a custom forecasting pipeline. That is the main value proposition in the paper: Chronos was pretrained once on many datasets and showed strong in-domain performance plus competitive or better zero-shot performance on unseen datasets.
2. You have many **related** forecasting tasks and want one reusable model instead of training a separate model per dataset or per series. The paper explicitly argues this can simplify production forecasting systems that need forecasts for many tasks.
3. The series has fairly standard patterns like seasonality and linear trend. In the paper’s qualitative analysis, Chronos handled seasonal patterns very well and did well on linear trends and additive/multiplicative combinations of trend and seasonality.

Chronos is a bad or weaker choice when:
1. **Exogenous or calendar** features matter a lot in the original Chronos setup. The paper says Chronos ignores explicit time and frequency features and treats the series simply as a sequence. So if holidays, promotions, weather, interventions, or known future covariates drive the outcome, original Chronos is a weaker fit. Newer follow-up work like **ChronosX** and **Chronos-2** adds covariate support
2. The series has patterns that clash with the tokenization/scaling design, especially:
    - sparse series with spikes or extreme outliers, where values can fall outside the representable range after scaling;
    - high-magnitude, low-variance series, where nearby values collapse into the same token and precision is lost.
3. The series has complicated pattern: **strong exponential trend** and **long-term seasonality**
4. **Latency or ultra-cheap** inference is critical. Chronos produces probabilistic forecasts by autoregressively sampling future trajectories, which is heavier than a simple local model or a light point forecaster.
5. **heterogeneous Global Model** 
    
> In summary, Use Chronos when "quick-and-dirty".






 
