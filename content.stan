data {
  int<lower=0> counts[256];
}

parameters {
  simplex[256] alpha;
  simplex[256] theta;
}

model {
  theta ~ dirichlet(alpha);
  counts ~ multinomial(theta);
}
