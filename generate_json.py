import json

variables = [
    'Chord',
    'Span',
    'Slope',
    'NonlinearCoefficient',
    'AngleOfAttack',
    'ElasticSupportPitchAngle',
    'Lift',
    'ChordwiseCoordinate',
    'SpringConstant',
    'ChordwiseSpringLocation',
    'DynamicPressure',
    'RampAngle']

with open('variables.json', 'w') as f:
    json.dump(variables, f, indent=2)

coupled = [
    'AerodynamicModel',
    'StructuralModel']
    #'AirfoilModel']

with open('coupled.json', 'w') as f:
    json.dump(coupled, f, indent=2)

models = {
    'AerodynamicModel': {
        'input': [
            'Chord',
            'DynamicPressure',
            'ElasticSupportPitchAngle',
            'Span',
            'Chord',
            'RampAngle',
            'Slope',
            'NonlinearCoefficient',
            'AngleOfAttack'],
        'output' : 'Lift'},
    'StructuralModel': {
        'input': [
            'Lift',
            'Chord',
            'ChordwiseCoordinate',
            {'name': 'SpringConstant', 'cardinality': 2},
            {'name': 'ChordwiseSpringLocation', 'cardinality': 2}],
        'output': 'ElasticSupportPitchAngle'}}
    #'AirfoilModel': {
    #    'input': [
    #        'Lift',
    #        'ElasticSupportPitchAngle'],
    #    'output': []}}

with open('models.json', 'w') as f:
    json.dump(models, f, indent=2)


values = {
    'Chord': 10,
    'AngleOfAttack': 0.26,
    'NonlinearCoefficient': 1.9056964116678532,
    'RampAngle': 5.1119125042852565,
    'Slope': 0.26,
    'Span': 100,
    'ChordwiseCoordinate': 0.25,
    'ChordwiseSpringLocation': [0.2, 0.7],
    'SpringConstant': [4000, 2000]}

with open('values.json', 'w') as f:
    json.dump(values, f, indent=2)
