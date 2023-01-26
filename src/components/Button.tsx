import * as React from 'react';
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  ViewStyle,
  StyleProp
} from 'react-native';

interface Props {
  children?: any,
  title?: any,
  onPress?: any,
  disabled?: boolean,
  style?: StyleProp<ViewStyle>,
}

export default function Button({ children, title, onPress, disabled, style }: Props) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.button, style]}
      disabled={disabled}
    >
      <Text style={styles.buttonText}>
        {title}
      </Text>
      {children}
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  button: {
    padding: 15,
    width: 200,
    backgroundColor: '#2196F3',
    marginBottom: 10
  },
  buttonText: {
    fontWeight: 'bold',
    textAlign: 'center',
  },
})
