import csv
import operator
import pprint
import math
import sys
import json
from collections import OrderedDict

priors = {} # P(B) probability that a telemetry submission contains addon B
likelihood = {} # P(A|B) probability that a telemetry submission contains addons A given that it contains addon B

def load_data():
    with open('data/addons.csv', 'r') as f:
        reader = csv.reader(f)
        total_count = 0

        for row in reader:
            freq = int(row[0])
            total_count += freq
            addons = filter(row[1:])

            for addon in addons:
                if addon in priors:
                    priors[addon] += freq
                else:
                    priors[addon] = freq

            for i in range(0, len(addons)):
                parent = addons[i]
                if not parent in likelihood:
                    likelihood[parent] = {}

                d = likelihood[parent]

                for j in range(0, len(addons)):
                    child = addons[j]
                    if not child in d:
                        d[child] = freq
                    else:
                        d[child] += freq
        filter_priors(total_count)
        normalize(total_count)

def filter_priors(total_count):
    # P(awesome addon | malware) might be very high so we try to remove
    # the bad addons by filtering on frequency

    for prior, value in priors.iteritems():
        if value < total_count*0.01:
            priors[prior] = sys.float_info.epsilon

def filter(addons):
    return list(set([a.strip() for a in addons if len(a) > 0]))

def normalize(total_count):
    for prior in priors:
        # use log to avoid numerical underflow
        priors[prior] = math.log(priors[prior] / float(total_count))

    for given, obs in likelihood.iteritems():
        total = obs[given]

        for ob, freq in obs.iteritems():
            assert(freq <= total)
            obs[ob] = math.log(freq / float(total))


def bayes_inference(addons):
    addons = filter(addons)
    updated_priors = {}

    for hypo in priors:
        score = priors[hypo]

        for addon in addons:
            term = likelihood[hypo][addon] if addon in likelihood[hypo] else 0 # additive smoothing
            score = score + term

        updated_priors[hypo] = score

    for addon in addons: # remove addon that we already have
        updated_priors[addon] = -sys.maxint

    return sorted(updated_priors.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]

def export():
    with open('data/probabilities.json', 'w') as f:
        top_priors = OrderedDict(sorted(priors.iteritems(), key=operator.itemgetter(1), reverse=True)[:200])
        top_likelihood = {}

        for prior, prob in top_priors.iteritems():
            top_likelihood[prior] = {obs: value for (obs, value)
                                     in likelihood[prior].iteritems()
                                     if obs in top_priors}

        json.dump({'priors': top_priors, 'likelihood': top_likelihood}, f, indent=2)


if __name__ == "__main__":
    load_data()
    export()
    pprint.pprint(bayes_inference([]))
