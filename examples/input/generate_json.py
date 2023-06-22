import json


variables = {
    'Chord': {'label': 'Chord'},
    'Span': {'label': 'Span'},
    'Slope': {'label': 'Slope'},
    'NonlinearCoefficient': {'label': 'Nonlinear coefficient'},
    'AngleOfAttack': {'label': 'Angle of attack'},
    'ElasticSupportPitchAngle': {'label': 'Elastic support pitch angle'},
    'Lift': {'label': 'Lift'},
    'ChordwiseCoordinate': {'label': 'Chordwise coordinate'},
    'SpringConstant': {'label': 'Spring constant'},
    'ChordwiseSpringLocation': {'label': 'Chordwise spring location'},
    'DynamicPressure': {'label': 'Dynamic pressure'},
    'RampAngle': {'label': 'Ramp angle'}}

with open('variables.json', 'w') as f:
    json.dump(variables, f, indent=2)


coupled = {
    'AerodynamicModel': {'label': 'Aerodynamic model'},
    'StructuralModel': {'label': 'Aerodynamic model'}}

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
