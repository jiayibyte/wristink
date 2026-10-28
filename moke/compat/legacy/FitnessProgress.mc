module FitnessProgress {
    function completion(value,goal){if(value==null || goal==null || goal<=0){return null;}var ratio=value.toFloat()/goal;return ratio<0 ? 0.0 : (ratio>1 ? 1.0 : ratio);}
}
