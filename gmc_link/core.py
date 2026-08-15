# gmc_link/core.py
"""
Core utilities for extracting camera ego-motion via ORB features and homography.
"""
import os

import cv2
import numpy as np

from .utils import warp_points


class ORBHomographyEngine:
    """
    Compute rigid background motion (ego-motion) between frames using ORB features
    and RANSAC homography estimation. Masking foreground objects ensures we
    only track the true camera motion.
    """

    # GMC_HGATE=1 sanity bounds (audit A9): 7/916 eval transitions emit wild H
    # (corner displacement up to 5592px vs legit ego p95 = 50-99px) that
    # cumulative composition spreads over ~4.3% of (frame,gap) ego slots.
    HGATE_PERSP_MAX = 1e-3   # |h31|, |h32| bound (near-affine ego on KITTI)
    HGATE_DISP_MAX = 150.0   # max image-corner displacement, px

    def __init__(self, max_features: int = 1500) -> None:
        # GMC_FEAT selects the keypoint detector/descriptor (default orb).
        # Same pipeline otherwise: BFMatcher + Lowe 0.7 + RANSAC homography.
        feat = os.environ.get("GMC_FEAT", "orb")
        if feat == "akaze":
            self.orb, norm = cv2.AKAZE_create(), cv2.NORM_HAMMING
        elif feat == "brisk":
            self.orb, norm = cv2.BRISK_create(), cv2.NORM_HAMMING
        elif feat == "sift":
            self.orb, norm = cv2.SIFT_create(nfeatures=max_features), cv2.NORM_L2
        else:
            self.orb, norm = cv2.ORB_create(max_features), cv2.NORM_HAMMING
        self.matcher = cv2.BFMatcher(norm, crossCheck=False)
        # last accepted H — constant-ego prior beats camera-froze (identity)
        # prior on a moving KITTI vehicle; reused on gate-reject and fallbacks.
        self.last_good_H = np.eye(3, dtype=np.float32)
        self.hgate_rejects = 0
        self.fallback_reuses = 0

    def _hgate_enabled(self) -> bool:
        return os.environ.get("GMC_HGATE") == "1"

    def _fallback_H(self) -> np.ndarray:
        if self._hgate_enabled():
            self.fallback_reuses += 1
            return self.last_good_H.copy()
        return np.eye(3, dtype=np.float32)

    def estimate_road_homography(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        prev_bboxes: list[tuple[float, float, float, float]] | None = None,
        road_band: float = 0.5,
    ) -> np.ndarray | None:
        """Ground-plane homography from road-region features (GMC_GROUND=1).

        The road IS a plane, so a homography fit to road-region correspondences
        is geometrically exact for ground-contact points — the parallax the
        global background fit cannot model (A14: 3-57px object-level error).
        Asphalt is low-texture for ORB, so this uses goodFeaturesToTrack +
        pyramidal LK on the lower image band (minus detection boxes).
        Returns 3x3 H or None (caller falls back to the global transform).
        """
        prev_gray = (cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                     if len(prev_frame.shape) == 3 else prev_frame)
        curr_gray = (cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
                     if len(curr_frame.shape) == 3 else curr_frame)
        h, w = prev_gray.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[int(h * road_band):, :] = 255
        if prev_bboxes:
            for bbox in prev_bboxes:
                x1, y1, x2, y2 = map(int, bbox)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    mask[y1:y2, x1:x2] = 0
        pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=600,
                                      qualityLevel=0.01, minDistance=7, mask=mask)
        if pts is None or len(pts) < 12:
            return None
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, pts, None,
                                              winSize=(21, 21), maxLevel=3)
        ok = st.ravel() == 1
        if ok.sum() < 12:
            return None
        H, _ = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 3.0)
        return None if H is None else H.astype(np.float32)

    def _h_is_degenerate(self, H: np.ndarray, shape) -> bool:
        if abs(float(H[2, 0])) > self.HGATE_PERSP_MAX or abs(float(H[2, 1])) > self.HGATE_PERSP_MAX:
            return True
        h, w = shape[:2]
        corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], dtype=np.float32)
        disp = np.linalg.norm(warp_points(corners, H) - corners, axis=1)
        return float(disp.max()) > self.HGATE_DISP_MAX

    def estimate_homography(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        prev_bboxes: list[tuple[float, float, float, float]] | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Estimate the 3x3 homography matrix H_prev_to_curr that transforms points
        from prev_frame to curr_frame coordinates.

        Returns:
            (H, bg_residual): H is 3x3 homography; bg_residual is (2,) median
            absolute warp residual of RANSAC inliers in pixels (background noise floor).
        """
        prev_gray = (
            cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            if len(prev_frame.shape) == 3
            else prev_frame
        )
        curr_gray = (
            cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            if len(curr_frame.shape) == 3
            else curr_frame
        )

        mask = None
        if prev_bboxes:
            h, w = prev_gray.shape
            mask = np.ones((h, w), dtype=np.uint8) * 255
            for bbox in prev_bboxes:
                x1, y1, x2, y2 = map(int, bbox)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    mask[y1:y2, x1:x2] = 0

        kp1, des1 = self.orb.detectAndCompute(prev_gray, mask=mask)
        kp2, des2 = self.orb.detectAndCompute(curr_gray, mask=None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return self._fallback_H(), np.zeros(2, dtype=np.float32)

        matches = self.matcher.knnMatch(des1, des2, k=2)
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.7 * n.distance:  # Lowe's ratio test
                    good_matches.append(m)
            elif len(match_pair) == 1:
                good_matches.append(match_pair[0])

        if len(good_matches) < 4:
            return self._fallback_H(), np.zeros(2, dtype=np.float32)

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(
            -1, 1, 2
        )
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(
            -1, 1, 2
        )

        # GMC_MODEL selects the ego motion model (default homography, 8 DOF).
        # affine (6) / similarity (4): consecutive-frame KITTI ego is
        # near-affine; fewer DOF kills the wild-H tail by construction
        # (screen 2026-08-14: similarity 0 wild vs homography 8, same speed).
        model = os.environ.get("GMC_MODEL", "homography")
        if model == "affine":
            A, inlier_mask = cv2.estimateAffine2D(
                src_pts, dst_pts, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            homography_matrix = None if A is None else np.vstack([A, [0, 0, 1]])
        elif model == "similarity":
            A, inlier_mask = cv2.estimateAffinePartial2D(
                src_pts, dst_pts, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            homography_matrix = None if A is None else np.vstack([A, [0, 0, 1]])
        else:
            homography_matrix, inlier_mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if homography_matrix is None:
            return self._fallback_H(), np.zeros(2, dtype=np.float32)

        # Compute background residual: median abs warp error of RANSAC inliers
        H = homography_matrix.astype(np.float32)

        if self._hgate_enabled():
            if self._h_is_degenerate(H, prev_gray.shape):
                self.hgate_rejects += 1
                return self.last_good_H.copy(), np.zeros(2, dtype=np.float32)
            self.last_good_H = H.copy()
        if inlier_mask is not None and inlier_mask.sum() > 0:
            inlier_idx = inlier_mask.ravel().astype(bool)
            src_inliers = src_pts[inlier_idx].reshape(-1, 2)
            dst_inliers = dst_pts[inlier_idx].reshape(-1, 2)
            warped_src = warp_points(src_inliers, H)
            residuals = np.abs(dst_inliers - warped_src)
            bg_residual = np.median(residuals, axis=0).astype(np.float32)
        else:
            bg_residual = np.zeros(2, dtype=np.float32)

        return H, bg_residual
