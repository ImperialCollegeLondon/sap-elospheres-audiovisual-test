import numpy as np


class PsychometricFunction():
    def __init__(self,
                 threshold_db=0,
                 prob_at_threshold=0.5,
                 slope_at_threshold=0.1,
                 probability_of_miss=0,
                 guess_probability=0):
        self.threshold_db = threshold_db
        self.prob_at_threshold = prob_at_threshold
        self.slope_at_threshold = slope_at_threshold
        self.probability_of_miss = probability_of_miss
        self.guess_probability = guess_probability

    def probe_response(self, probe_level_db, num_responses=1):
        if self.prob_at_threshold != 0.5:
            raise NotImplementedError
        if self.probability_of_miss != 0:
            raise NotImplementedError
        if self.guess_probability != 0:
            raise NotImplementedError

        L = 1  # maximum value of the functions
        k = self.slope_at_threshold
        x0 = self.threshold_db
        x = probe_level_db
        prob_of_success = L / (1 + np.exp(-k * (x-x0)))
        return np.random.binomial(1, prob_of_success, size=num_responses)


        # pscale=1-qq(4,:)-qq(5,:);  % prob range excluding miss and lapse probs
        # pstd=(qq(1,:)-qq(5,:))./pscale; % prob target compensating for miss and lapse probs
        # sstd=qq(3,:)./pscale; % slope compensating for miss and lapse probs
        # beta=sstd./(pstd.*(1-pstd));
        # px=(1+exp(repmat(beta.*qq(2,:)+log((1-pstd)./pstd),nx,1)-x(:)*beta)).^(-1);
