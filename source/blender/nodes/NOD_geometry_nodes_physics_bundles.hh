/* SPDX-FileCopyrightText: 2025 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

#include "BLI_string_ref.hh"

#include "NOD_bundle_type_fwd.hh"

namespace blender::nodes::physics_bundles {

class MeshColliderBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Collider.Mesh";
  static const FlatBundleTypePtr &get_bundle_type();
};

class CollisionContactsBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.CollisionContacts";
  static const FlatBundleTypePtr &get_bundle_type();
};

class DampingBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Damping";
  static const FlatBundleTypePtr &get_bundle_type();
};

class PinPositionBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.PinPosition";
  static const FlatBundleTypePtr &get_bundle_type();
};

class PinRotationBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.PinRotation";
  static const FlatBundleTypePtr &get_bundle_type();
};

class RodStretchShearBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.RodStretchShear";
  static const FlatBundleTypePtr &get_bundle_type();
};

class RodBendTwistBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.RodBendTwist";
  static const FlatBundleTypePtr &get_bundle_type();
};

class EdgeLengthConstraintBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.EdgeLength";
  static const FlatBundleTypePtr &get_bundle_type();
};

class CrossEdgeLengthConstraintBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Constraint.CrossEdgeLength";
  static const FlatBundleTypePtr &get_bundle_type();
};

/** This is currently not used by built-in nodes but is used in essential assets. */
class ForceBundle {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.Force";
  static const FlatBundleTypePtr &get_bundle_type();
};

/** This is currently not used by built-in nodes but is used in essential assets. */
class CustomGeometryEffector {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.CustomEffector.Geometry";
  static const FlatBundleTypePtr &get_bundle_type();
};

/** This is currently not used by built-in nodes but is used in essential assets. */
class CustomWorldEffector {
 public:
  static constexpr StringRefNull name = "EasyFormStudio.CustomEffector.World";
  static const FlatBundleTypePtr &get_bundle_type();
};

}  // namespace blender::nodes::physics_bundles
