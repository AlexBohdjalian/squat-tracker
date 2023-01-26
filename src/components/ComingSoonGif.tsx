import React from "react";
import { Text, View, Image, StyleSheet } from 'react-native';

const AddGifImage = () => {
  return (
    <View style={Styles.container}>
      <Image
        source={require('../assets/images/oh-no.gif')}
        style={Styles.image}
      />
      <Text>Coming Soon!</Text>
    </View>
  );
}

const Styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    margin: 25,
  },
  image: {
    width: '100%',
    height: undefined,
    aspectRatio: 1,
  },
})

export default AddGifImage;