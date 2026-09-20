# Geometry observations (P2)
from .geometry_config import (
    GeometryConfig, DEFAULT_CONFIG, to_dict,
    REL_LEFT_OF, REL_RIGHT_OF, REL_ABOVE, REL_BELOW,
    REL_OVERLAPPING, REL_CONTAINED_BY, REL_CONTAINS, REL_SAME_POSITION,
    ALL_RELATIONS, INVERSE_RELATIONS, SYMMETRIC_RELATIONS,
)
from .geometry_observation import (
    SingleObservationGeometry, PairwiseRelation, PageGeometryBundle,
)
from .geometry_engine import (
    compute_single, compute_pairwise, compute_page_bundle,
    verify_symmetry, expected_inverse,
)
